/**
 * Frontend Tracing Logger
 * 
 * 与后端 OpenTelemetry 集成的前端追踪系统。
 * 通过 X-Trace-ID header 将前端追踪与后端关联。
 * 
 * 使用方式：
 * ```typescript
 * // 1. 开始一个新的追踪（通常在用户操作开始时）
 * const trace = logger.startTrace().withContext({ page: 'investment-summary' });
 * 
 * // 2. 创建一个 span 来追踪具体操作
 * const span = trace.startSpan('fetch_summary', { companyId: '123' });
 * try {
 *   const result = await fetchData();
 *   span.end({ status: 'success', dataSize: result.length });
 * } catch (error) {
 *   span.end({ status: 'error', error: error.message });
 * }
 * 
 * // 3. 获取 trace ID 用于 API 请求头
 * const traceId = trace.getTraceId();
 * fetch(url, { headers: { 'X-Trace-ID': traceId } });
 * ```
 */

export interface LogContext {
  [key: string]: unknown;
}

export interface SpanData {
  name: string;
  traceId: string;
  spanId: string;
  parentSpanId: string | null;
  startTime: number;
  endTime?: number;
  duration?: number;
  attributes: LogContext;
  status: 'running' | 'success' | 'error';
  events: SpanEvent[];
}

export interface SpanEvent {
  name: string;
  timestamp: number;
  attributes?: LogContext;
}

/**
 * 生成符合 OpenTelemetry 规范的 Trace ID (32 hex chars)
 */
function generateTraceId(): string {
  const hex = () => Math.random().toString(16).substring(2, 10);
  return hex() + hex() + hex() + hex();
}

/**
 * 生成 Span ID (16 hex chars)
 */
function generateSpanId(): string {
  const hex = () => Math.random().toString(16).substring(2, 10);
  return hex() + hex();
}

/**
 * Span 类 - 表示一个可追踪的操作单元
 */
export class Span {
  private data: SpanData;
  private logger: Logger;
  private ended: boolean = false;

  constructor(
    name: string,
    traceId: string,
    parentSpanId: string | null,
    attributes: LogContext,
    logger: Logger
  ) {
    this.data = {
      name,
      traceId,
      spanId: generateSpanId(),
      parentSpanId,
      startTime: performance.now(),
      attributes,
      status: 'running',
      events: [],
    };
    this.logger = logger;
    
    // 记录 span 开始
    this.logger.debug(`[Span Start] ${name}`, {
      spanId: this.data.spanId,
      parentSpanId,
      ...attributes,
    });
  }

  /**
   * 添加一个事件到 span（例如：关键节点、状态变化）
   */
  addEvent(name: string, attributes?: LogContext): this {
    if (this.ended) {
      this.logger.warn(`Span already ended: ${this.data.name}`);
      return this;
    }
    
    this.data.events.push({
      name,
      timestamp: performance.now(),
      attributes,
    });
    
    this.logger.debug(`[Span Event] ${this.data.name}/${name}`, {
      spanId: this.data.spanId,
      ...attributes,
    });
    
    return this;
  }

  /**
   * 设置 span 属性
   */
  setAttribute(key: string, value: unknown): this {
    this.data.attributes[key] = value;
    return this;
  }

  /**
   * 结束 span 并记录结果
   */
  end(result?: { status?: 'success' | 'error'; [key: string]: unknown }): SpanData {
    if (this.ended) {
      this.logger.warn(`Span already ended: ${this.data.name}`);
      return this.data;
    }
    
    this.ended = true;
    this.data.endTime = performance.now();
    this.data.duration = this.data.endTime - this.data.startTime;
    this.data.status = result?.status || 'success';
    
    // 合并结束时的属性
    if (result) {
      const { status, ...rest } = result;
      Object.assign(this.data.attributes, rest);
    }
    
    // 记录 span 结束
    const level = this.data.status === 'error' ? 'error' : 'info';
    this.logger[level](`[Span End] ${this.data.name}`, {
      spanId: this.data.spanId,
      duration: `${this.data.duration.toFixed(2)}ms`,
      status: this.data.status,
      eventsCount: this.data.events.length,
      ...this.data.attributes,
    });
    
    return this.data;
  }

  getSpanId(): string {
    return this.data.spanId;
  }

  getTraceId(): string {
    return this.data.traceId;
  }

  getData(): SpanData {
    return { ...this.data };
  }
}

/**
 * Logger 类 - 支持结构化日志和追踪
 */
class Logger {
  private context: LogContext = {};
  private traceId: string | null = null;
  private currentSpanId: string | null = null;
  private spans: Map<string, SpanData> = new Map();

  constructor(context: LogContext = {}) {
    this.context = context;
  }

  /**
   * 创建带有新上下文的子 Logger
   */
  withContext(context: LogContext): Logger {
    const newLogger = new Logger({ ...this.context, ...context });
    newLogger.traceId = this.traceId;
    newLogger.currentSpanId = this.currentSpanId;
    newLogger.spans = this.spans;
    return newLogger;
  }

  /**
   * 开始一个新的 Trace（通常在用户操作开始时调用）
   */
  startTrace(traceId?: string): Logger {
    const newLogger = new Logger({ ...this.context });
    newLogger.traceId = traceId || generateTraceId();
    newLogger.spans = new Map();
    
    newLogger.info('[Trace Start]', { traceId: newLogger.traceId });
    
    return newLogger;
  }

  /**
   * 创建一个新的 Span
   */
  startSpan(name: string, attributes: LogContext = {}): Span {
    if (!this.traceId) {
      // 自动创建 trace
      this.traceId = generateTraceId();
      this.info('[Trace Auto-Start]', { traceId: this.traceId });
    }
    
    const span = new Span(
      name,
      this.traceId,
      this.currentSpanId,
      attributes,
      this
    );
    
    this.currentSpanId = span.getSpanId();
    this.spans.set(span.getSpanId(), span.getData());
    
    return span;
  }

  /**
   * 获取当前 Trace ID（用于 API 请求头）
   */
  getTraceId(): string | null {
    return this.traceId;
  }

  /**
   * 获取当前 Span ID
   */
  getCurrentSpanId(): string | null {
    return this.currentSpanId;
  }

  /**
   * 生成用于 API 请求的 headers
   */
  getTraceHeaders(): Record<string, string> {
    const headers: Record<string, string> = {};
    if (this.traceId) {
      headers['X-Trace-ID'] = this.traceId;
    }
    if (this.currentSpanId) {
      headers['X-Span-ID'] = this.currentSpanId;
    }
    return headers;
  }

  /**
   * 核心日志方法
   */
  private log(level: 'info' | 'warn' | 'error' | 'debug', message: string, meta?: LogContext) {
    const timestamp = new Date().toISOString();
    const logEntry = {
      timestamp,
      level,
      message,
      trace_id: this.traceId,
      span_id: this.currentSpanId,
      service: 'mem-dashboard-frontend',
      ...this.context,
      ...meta,
    };
    
    // 开发环境：彩色输出 + 对象展开
    if (import.meta.env.DEV) {
      const colors = {
        info: '#3b82f6',    // blue
        warn: '#f59e0b',    // amber
        error: '#ef4444',   // red
        debug: '#6b7280',   // gray
      };
      
      const style = `color: ${colors[level]}; font-weight: bold`;
      const traceStyle = 'color: #8b5cf6; font-weight: normal';
      const spanStyle = 'color: #10b981; font-weight: normal';
      
      // 构建前缀
      let prefix = `%c[${level.toUpperCase()}]`;
      const styles = [style];
      
      if (this.traceId) {
        prefix += ` %c[T:${this.traceId.slice(0, 8)}]`;
        styles.push(traceStyle);
      }
      if (this.currentSpanId) {
        prefix += ` %c[S:${this.currentSpanId.slice(0, 8)}]`;
        styles.push(spanStyle);
      }
      
      const hasMeta = meta && Object.keys(meta).length > 0;
      const hasContext = Object.keys(this.context).length > 0;
      
      if (hasMeta || hasContext) {
        console.groupCollapsed(`${prefix} %c${message}`, ...styles, 'color: inherit');
        if (this.traceId) console.log('Trace ID:', this.traceId);
        if (this.currentSpanId) console.log('Span ID:', this.currentSpanId);
        if (hasContext) console.log('Context:', this.context);
        if (hasMeta) console.log('Data:', meta);
        console.groupEnd();
      } else {
        console.log(`${prefix} %c${message}`, ...styles, 'color: inherit');
      }
    } else {
      // 生产环境：单行 JSON（便于日志聚合）
      console.log(JSON.stringify(logEntry));
    }
  }

  info(message: string, meta?: LogContext) { this.log('info', message, meta); }
  error(message: string, meta?: LogContext) { this.log('error', message, meta); }
  warn(message: string, meta?: LogContext) { this.log('warn', message, meta); }
  debug(message: string, meta?: LogContext) { this.log('debug', message, meta); }

  /**
   * 便捷方法：追踪一个异步操作
   */
  async traceAsync<T>(
    name: string,
    operation: () => Promise<T>,
    attributes: LogContext = {}
  ): Promise<T> {
    const span = this.startSpan(name, attributes);
    try {
      const result = await operation();
      span.end({ status: 'success' });
      return result;
    } catch (error) {
      span.end({ 
        status: 'error', 
        error: error instanceof Error ? error.message : String(error) 
      });
      throw error;
    }
  }

  /**
   * 获取完整的追踪数据（用于调试或发送到后端）
   */
  getTraceData(): { traceId: string | null; spans: SpanData[] } {
    return {
      traceId: this.traceId,
      spans: Array.from(this.spans.values()),
    };
  }
}

// 导出全局 logger 实例
export const logger = new Logger();

// 导出类型和类供高级用法
export { Logger, generateTraceId, generateSpanId };
