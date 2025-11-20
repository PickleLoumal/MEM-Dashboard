(function() {
    class PolicyFeedManager {
        constructor(apiClient) {
            this.apiClient = apiClient;
            this.country = 'US';
            this.feedElement = document.getElementById('policy-updates-feed');
            this.lastSyncElement = document.getElementById('policy-updates-last-sync');
            this.sourceElement = document.getElementById('policy-updates-source');
            this.statusDot = document.getElementById('policy-updates-status-dot');
            this.activeCountElement = document.getElementById('policy-active-count');
            this.themeElement = document.getElementById('policy-dominant-theme');
            this.impactElement = document.getElementById('policy-impact-signal');
            this.refreshButton = document.getElementById('policy-updates-refresh');
            this.isRefreshing = false;

            if (this.refreshButton) {
                this.refreshButton.addEventListener('click', () => this.handleManualRefresh());
            }
        }

        async handleManualRefresh() {
            if (this.isRefreshing) {
                return;
            }
            await this.refreshFeed(this.country, true);
        }

        async refreshFeed(country = 'US', isManual = false) {
            if (!this.feedElement) {
                this.feedElement = document.getElementById('policy-updates-feed');
            }

            if (!this.feedElement || !this.apiClient) {
                console.warn('PolicyFeedManager missing DOM container or API client');
                return false;
            }

            this.country = country;
            this.setLoadingState(true, isManual);

            try {
                const payload = await this.apiClient.getPolicyUpdates(country);
                const updates = this.normalizePayload(payload);
                this.renderUpdates(updates);
                this.renderInsights(updates);
                this.updateMeta(payload, updates);
                this.setStatusDot(true);
                return true;
            } catch (error) {
                console.error('Policy feed refresh failed:', error);
                this.renderError(error);
                this.setStatusDot(false);
                return false;
            } finally {
                this.setLoadingState(false, isManual);
            }
        }

        setLoadingState(isLoading, isManual) {
            this.isRefreshing = isLoading;
            if (this.refreshButton) {
                this.refreshButton.disabled = isLoading;
                this.refreshButton.textContent = isLoading ? 'Refreshing...' : 'Refresh';
            }

            if (isLoading && this.feedElement && !isManual) {
                this.feedElement.innerHTML = this.skeletonTemplate();
            }

        }

        updateMeta(payload, updates) {
            if (this.lastSyncElement) {
                const lastUpdated =
                    (payload && payload.last_updated) ||
                    (updates[0] && updates[0].timestamp) ||
                    new Date().toISOString();
                this.lastSyncElement.textContent = this.formatTimestamp(lastUpdated);
            }

            if (this.sourceElement) {
                const feedSource = (payload && payload.source) || (updates[0] && updates[0].source) || 'Federal Register';
                this.sourceElement.textContent = feedSource;
            }
        }

        setStatusDot(isOnline) {
            if (!this.statusDot) {
                this.statusDot = document.getElementById('policy-updates-status-dot');
            }
            if (!this.statusDot) {
                return;
            }
            if (isOnline) {
                this.statusDot.classList.remove('offline');
            } else {
                this.statusDot.classList.add('offline');
            }
        }

        normalizePayload(payload) {
            if (!payload) {
                return [];
            }

            const records = Array.isArray(payload.data)
                ? payload.data
                : Array.isArray(payload.results)
                ? payload.results
                : [];

            return records
                .filter(Boolean)
                .map((record) => {
                    const tags = this.normalizeTags(record);
                    return {
                        title: record.title || record.headline || 'Untitled Policy Signal',
                        summary: record.summary || record.description || record.notes || 'No summary provided.',
                        category: record.category || record.type || record.theme || 'General Policy',
                        impact_level: this.normalizeImpact(record),
                        tags,
                        status: this.normalizeStatus(record),
                        source: record.source || payload.source || 'Federal Register',
                        timestamp:
                            record.timestamp ||
                            record.publication_date ||
                            record.updated_at ||
                            payload.last_updated ||
                            new Date().toISOString(),
                        link: record.link || record.html_url || null,
                    };
                });
        }

        normalizeImpact(record) {
            const impact = (record.impact_level || record.impact || '').toString().toLowerCase();
            if (impact === 'high' || record.significant === true) {
                return 'high';
            }
            if (impact === 'low') {
                return 'low';
            }
            return 'medium';
        }

        normalizeStatus(record) {
            const status = (record.status || '').toString().toLowerCase();
            if (status) {
                return status;
            }
            return record.significant ? 'active' : 'watching';
        }

        normalizeTags(record) {
            if (Array.isArray(record.tags)) {
                return record.tags.filter(Boolean).slice(0, 5);
            }
            if (Array.isArray(record.topics)) {
                return record.topics.filter(Boolean).slice(0, 5);
            }
            if (typeof record.tags === 'string') {
                return record.tags
                    .split(',')
                    .map((tag) => tag.trim())
                    .filter(Boolean)
                    .slice(0, 5);
            }
            return [];
        }

        renderUpdates(updates) {
            if (!this.feedElement) {
                return;
            }

            if (!updates.length) {
                this.feedElement.innerHTML = '<div class="policy-empty-state">No live policy directives detected in the past 48 hours.</div>';
                return;
            }

            const limitedUpdates = updates.slice(0, 5);
            this.feedElement.innerHTML = '';

            limitedUpdates.forEach((entry, index) => {
                const itemEl = document.createElement('div');
                itemEl.className = 'policy-item';

                itemEl.appendChild(this.renderHeader(entry));

                const summaryEl = document.createElement('p');
                summaryEl.className = 'policy-item-summary';
                summaryEl.textContent = entry.summary;
                itemEl.appendChild(summaryEl);

                if (entry.tags && entry.tags.length) {
                    const tagsWrapper = document.createElement('div');
                    tagsWrapper.className = 'policy-tags';
                    entry.tags.forEach((tag) => {
                        const tagEl = document.createElement('span');
                        tagEl.className = 'policy-tag';
                        tagEl.textContent = tag;
                        tagsWrapper.appendChild(tagEl);
                    });
                    itemEl.appendChild(tagsWrapper);
                }

                itemEl.appendChild(this.renderFooter(entry));
                this.feedElement.appendChild(itemEl);

                if (index !== limitedUpdates.length - 1) {
                    const divider = document.createElement('hr');
                    divider.className = 'policy-feed-divider';
                    this.feedElement.appendChild(divider);
                }
            });
        }

        renderHeader(entry) {
            const headerEl = document.createElement('div');
            headerEl.className = 'policy-item-header';

            const titleWrapper = document.createElement('div');
            const titleEl = document.createElement('div');
            titleEl.className = 'policy-item-title';
            if (entry.link) {
                const link = document.createElement('a');
                link.href = entry.link;
                link.target = '_blank';
                link.rel = 'noopener noreferrer';
                link.textContent = entry.title;
                titleEl.appendChild(link);
            } else {
                titleEl.textContent = entry.title;
            }

            const metaEl = document.createElement('div');
            metaEl.className = 'policy-item-meta';
            metaEl.textContent = `${entry.category} • ${this.formatTimestamp(entry.timestamp)}`;

            titleWrapper.appendChild(titleEl);
            titleWrapper.appendChild(metaEl);

            const impactEl = document.createElement('span');
            impactEl.className = `policy-impact-badge ${entry.impact_level}`;
            impactEl.textContent = this.titleCase(entry.impact_level);

            headerEl.appendChild(titleWrapper);
            headerEl.appendChild(impactEl);

            return headerEl;
        }

        renderFooter(entry) {
            const footerEl = document.createElement('div');
            footerEl.className = 'policy-item-footer';

            const sourceEl = document.createElement('span');
            sourceEl.textContent = `Source: ${entry.source}`;

            const statusEl = document.createElement('span');
            statusEl.className = `policy-status status-${entry.status}`;
            statusEl.textContent = `Status: ${this.titleCase(entry.status)}`;

            footerEl.appendChild(sourceEl);
            footerEl.appendChild(statusEl);
            return footerEl;
        }

        renderInsights(updates) {
            const countText = updates.length ? String(updates.length) : '0';
            if (this.activeCountElement) {
                this.activeCountElement.textContent = countText;
            }
            if (this.themeElement) {
                this.themeElement.textContent = this.getDominantTheme(updates);
            }
            if (this.impactElement) {
                this.impactElement.textContent = this.getImpactSignal(updates);
            }
        }

        getDominantTheme(updates) {
            if (!updates.length) {
                return '--';
            }
            const tally = updates.reduce((acc, entry) => {
                const key = (entry.category || 'General Policy').trim();
                acc[key] = (acc[key] || 0) + 1;
                return acc;
            }, {});

            return Object.entries(tally)
                .sort((a, b) => b[1] - a[1])
                .map(([label]) => label)[0];
        }

        getImpactSignal(updates) {
            if (!updates.length) {
                return '--';
            }
            const scoreMap = { high: 3, medium: 2, low: 1 };
            const best = updates.reduce(
                (state, entry) => {
                    const level = entry.impact_level || 'medium';
                    const score = scoreMap[level] || 0;
                    if (score > state.score) {
                        return { level, score };
                    }
                    return state;
                },
                { level: 'low', score: 0 }
            );

            const matches = updates.filter((entry) => entry.impact_level === best.level).length;
            return `${this.titleCase(best.level)} · ${matches}`;
        }

        renderError(error) {
            if (!this.feedElement) {
                return;
            }
            this.feedElement.innerHTML = `<div class="policy-error-state"><strong>Unable to load policy feed.</strong><br>${
                error && error.message ? error.message : 'Please try again later.'
            }</div>`;
        }

        skeletonTemplate() {
            return `
                <div class="policy-skeleton">
                    <div class="policy-skeleton-line w-10/12"></div>
                    <div class="policy-skeleton-line w-8/12"></div>
                    <div class="policy-skeleton-line w-6/12"></div>
                </div>
            `;
        }

        formatTimestamp(value) {
            if (!value) {
                return '--';
            }
            try {
                const parsedDate = new Date(value);
                if (Number.isNaN(parsedDate.getTime())) {
                    return value;
                }
                return new Intl.DateTimeFormat('en-US', {
                    month: 'short',
                    day: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit',
                }).format(parsedDate);
            } catch (error) {
                console.warn('Unable to format policy timestamp:', error);
                return value;
            }
        }

        titleCase(text = '') {
            return text
                ? text.replace(/\w\S*/g, (word) => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
                : '';
        }
    }

    function initializePolicyFeedManager() {
        if (window.policyFeedManager || !document.getElementById('policy-updates-card')) {
            return;
        }

        const tryAttach = () => {
            if (window.memApiClient) {
                window.policyFeedManager = new PolicyFeedManager(window.memApiClient);
                window.policyFeedManager.refreshFeed('US');
            } else {
                setTimeout(tryAttach, 200);
            }
        };

        tryAttach();
    }

    document.addEventListener('DOMContentLoaded', initializePolicyFeedManager);

    function attachPrototypeExtension() {
        if (window.MEMApiClient && !window.MEMApiClient.prototype.updatePolicyUpdatesBoard) {
            window.MEMApiClient.prototype.updatePolicyUpdatesBoard = async function(country = 'US') {
                if (!window.policyFeedManager) {
                    window.policyFeedManager = new PolicyFeedManager(this);
                }
                return window.policyFeedManager.refreshFeed(country);
            };
        } else if (!window.MEMApiClient) {
            setTimeout(attachPrototypeExtension, 200);
        }
    }

    attachPrototypeExtension();

    window.PolicyFeedManager = PolicyFeedManager;
})();
