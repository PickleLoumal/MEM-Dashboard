"""
FRED US Indicator Action Mixins

指标端点 Mixins - 按类别组织的特定指标端点。
"""

from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response


class MonetaryIndicatorsMixin:
    """货币政策相关指标"""
    
    @action(detail=False, methods=['get'], url_path='m2')
    def m2_money_supply(self, request: Request) -> Response:
        """M2货币供应量 - GET /api/fred-us/m2/"""
        return self._get_specific_indicator('M2SL', request)
    
    @action(detail=False, methods=['get'], url_path='m1')
    def m1_money_supply(self, request: Request) -> Response:
        """M1货币供应量 - GET /api/fred-us/m1/"""
        return self._get_specific_indicator('M1SL', request)
    
    @action(detail=False, methods=['get'], url_path='m2v')
    def m2_velocity(self, request: Request) -> Response:
        """M2货币流通速度 - GET /api/fred-us/m2v/"""
        return self._get_specific_indicator('M2V', request)
    
    @action(detail=False, methods=['get'], url_path='monetary-base')
    def monetary_base(self, request: Request) -> Response:
        """货币基础 - GET /api/fred-us/monetary-base/"""
        return self._get_specific_indicator('BOGMBASE', request)
    
    @action(detail=False, methods=['get'], url_path='fed-funds')
    def fed_funds_rate(self, request: Request) -> Response:
        """联邦基金利率 - GET /api/fred-us/fed-funds/"""
        return self._get_specific_indicator('FEDFUNDS', request)
    
    @action(detail=False, methods=['get'], url_path='federal-funds-rate')
    def federal_funds_rate(self, request: Request) -> Response:
        """联邦基金利率 (Money Supply) - GET /api/fred-us/federal-funds-rate/"""
        return self._get_specific_indicator('FEDFUNDS', request)
    
    @action(detail=False, methods=['get'], url_path='m2-money-supply')
    def m2_money_supply_alias(self, request: Request) -> Response:
        """M2货币供应量 - GET /api/fred-us/m2-money-supply/"""
        return self._get_specific_indicator('M2SL', request)
    
    @action(detail=False, methods=['get'], url_path='fed-balance-sheet')
    def fed_balance_sheet(self, request: Request) -> Response:
        """美联储资产负债表总资产 - GET /api/fred-us/fed-balance-sheet/"""
        return self._get_specific_indicator('WALCL', request)
    
    @action(detail=False, methods=['get'], url_path='bank-lending-standards')
    def bank_lending_standards(self, request: Request) -> Response:
        """银行贷款标准 - GET /api/fred-us/bank-lending-standards/"""
        return self._get_specific_indicator('DRTSCIS', request)
    
    @action(detail=False, methods=['get'], url_path='commercial-bank-loans')
    def commercial_bank_loans(self, request: Request) -> Response:
        """商业银行贷款和租赁总额 - GET /api/fred-us/commercial-bank-loans/"""
        return self._get_specific_indicator('TOTLL', request)
    
    @action(detail=False, methods=['get'], url_path='interest-rate-reserve-balances')
    def interest_rate_reserve_balances(self, request: Request) -> Response:
        """准备金余额利率 - GET /api/fred-us/interest-rate-reserve-balances/"""
        return self._get_specific_indicator('IORB', request)
    
    @action(detail=False, methods=['get'], url_path='overnight-reverse-repo')
    def overnight_reverse_repo(self, request: Request) -> Response:
        """隔夜逆回购协议 - GET /api/fred-us/overnight-reverse-repo/"""
        return self._get_specific_indicator('RRPONTSYD', request)
    
    @action(detail=False, methods=['get'], url_path='m1-money-supply')
    def m1_money_supply_alias(self, request: Request) -> Response:
        """M1货币供应量 - GET /api/fred-us/m1-money-supply/"""
        return self._get_specific_indicator('M1SL', request)


class DebtIndicatorsMixin:
    """债务相关指标"""
    
    @action(detail=False, methods=['get'], url_path='debt-to-gdp')
    def debt_to_gdp(self, request: Request) -> Response:
        """债务与GDP比率 - GET /api/fred-us/debt-to-gdp/"""
        return self._get_specific_indicator('GFDEGDQ188S', request)
    
    # Consumer and Household Debt
    @action(detail=False, methods=['get'], url_path='household-debt-gdp')
    def household_debt_gdp(self, request: Request) -> Response:
        """家庭债务占GDP比重 - GET /api/fred-us/household-debt-gdp/"""
        return self._get_specific_indicator('HDTGPDUSQ163N', request)

    @action(detail=False, methods=['get'], url_path='debt-service-ratio')
    def debt_service_ratio(self, request: Request) -> Response:
        """家庭债务偿还比率 - GET /api/fred-us/debt-service-ratio/"""
        return self._get_specific_indicator('TDSP', request)

    @action(detail=False, methods=['get'], url_path='mortgage-debt')
    def mortgage_debt_outstanding(self, request: Request) -> Response:
        """抵押贷款债务未偿余额 - GET /api/fred-us/mortgage-debt/"""
        return self._get_specific_indicator('MDOAH', request)

    @action(detail=False, methods=['get'], url_path='credit-card-debt')
    def credit_card_balances(self, request: Request) -> Response:
        """信用卡债务余额 - GET /api/fred-us/credit-card-debt/"""
        return self._get_specific_indicator('RCCCBBALTOT', request)

    @action(detail=False, methods=['get'], url_path='student-loans')
    def student_loans(self, request: Request) -> Response:
        """学生贷款 - GET /api/fred-us/student-loans/"""
        return self._get_specific_indicator('SLOASM', request)

    @action(detail=False, methods=['get'], url_path='consumer-credit')
    def total_consumer_credit(self, request: Request) -> Response:
        """总消费者信贷 - GET /api/fred-us/consumer-credit/"""
        return self._get_specific_indicator('TOTALSL', request)

    @action(detail=False, methods=['get'], url_path='total-debt')
    def total_household_debt(self, request: Request) -> Response:
        """家庭总债务 - GET /api/fred-us/total-debt/"""
        return self._get_specific_indicator('DTCOLNVHFNM', request)

    # Government Debts
    @action(detail=False, methods=['get'], url_path='federal-debt-total')
    def federal_debt_total(self, request: Request) -> Response:
        """联邦债务总额 - GET /api/fred-us/federal-debt-total/"""
        return self._get_specific_indicator('GFDEBTN', request)

    @action(detail=False, methods=['get'], url_path='federal-debt-gdp-ratio')
    def federal_debt_gdp_ratio(self, request: Request) -> Response:
        """联邦债务占GDP比例 - GET /api/fred-us/federal-debt-gdp-ratio/"""
        return self._get_specific_indicator('GFDEGDQ188S', request)

    @action(detail=False, methods=['get'], url_path='federal-surplus-deficit')
    def federal_surplus_deficit(self, request: Request) -> Response:
        """联邦盈余或赤字 - GET /api/fred-us/federal-surplus-deficit/"""
        return self._get_specific_indicator('MTSDS133FMS', request)

    @action(detail=False, methods=['get'], url_path='gross-federal-debt')
    def gross_federal_debt(self, request: Request) -> Response:
        """联邦总债务 - GET /api/fred-us/gross-federal-debt/"""
        return self._get_specific_indicator('FYGFD', request)

    @action(detail=False, methods=['get'], url_path='federal-interest-gdp')
    def federal_interest_gdp(self, request: Request) -> Response:
        """联邦利息支出占GDP比例 - GET /api/fred-us/federal-interest-gdp/"""
        return self._get_specific_indicator('FYOIGDA188S', request)

    @action(detail=False, methods=['get'], url_path='federal-debt-public-gdp')
    def federal_debt_public_gdp(self, request: Request) -> Response:
        """联邦公共债务占GDP比例 - GET /api/fred-us/federal-debt-public-gdp/"""
        return self._get_specific_indicator('FYGFGDQ188S', request)

    @action(detail=False, methods=['get'], url_path='government-consumer-credit')
    def government_consumer_credit(self, request: Request) -> Response:
        """政府消费者信贷 - GET /api/fred-us/government-consumer-credit/"""
        return self._get_specific_indicator('TOTALGOV', request)

    # Government Deficit Financing
    @action(detail=False, methods=['get'], url_path='federal-debt-total-gdf')
    def federal_debt_total_gdf(self, request: Request) -> Response:
        """联邦债务总额 (GDF) - GET /api/fred-us/federal-debt-total-gdf/"""
        return self._get_specific_indicator('GFDEBTN', request)
    
    @action(detail=False, methods=['get'], url_path='federal-debt-gdp-ratio-gdf')
    def federal_debt_gdp_ratio_gdf(self, request: Request) -> Response:
        """联邦债务占GDP比例 (GDF) - GET /api/fred-us/federal-debt-gdp-ratio-gdf/"""
        return self._get_specific_indicator('GFDEGDQ188S', request)
    
    @action(detail=False, methods=['get'], url_path='federal-surplus-deficit-gdf')
    def federal_surplus_deficit_gdf(self, request: Request) -> Response:
        """联邦盈余或赤字 (GDF) - GET /api/fred-us/federal-surplus-deficit-gdf/"""
        return self._get_specific_indicator('MTSDS133FMS', request)
    
    @action(detail=False, methods=['get'], url_path='federal-tax-receipts')
    def federal_tax_receipts(self, request: Request) -> Response:
        """联邦政府当期税收 - GET /api/fred-us/federal-tax-receipts/"""
        return self._get_specific_indicator('W006RC1Q027SBEA', request)
    
    @action(detail=False, methods=['get'], url_path='federal-net-outlays')
    def federal_net_outlays(self, request: Request) -> Response:
        """联邦净支出 - GET /api/fred-us/federal-net-outlays/"""
        return self._get_specific_indicator('FYONET', request)
    
    @action(detail=False, methods=['get'], url_path='federal-current-expenditures')
    def federal_current_expenditures(self, request: Request) -> Response:
        """联邦政府当期支出 - GET /api/fred-us/federal-current-expenditures/"""
        return self._get_specific_indicator('FGEXPND', request)
    
    @action(detail=False, methods=['get'], url_path='federal-current-receipts')
    def federal_current_receipts(self, request: Request) -> Response:
        """联邦政府当期收入 - GET /api/fred-us/federal-current-receipts/"""
        return self._get_specific_indicator('FGRECPT', request)
    
    @action(detail=False, methods=['get'], url_path='excess-reserves')
    def excess_reserves(self, request: Request) -> Response:
        """存款机构超额准备金 - GET /api/fred-us/excess-reserves/"""
        return self._get_specific_indicator('EXCSRESNW', request)

    # Corporate Debt
    @action(detail=False, methods=['get'], url_path='corporate-debt-securities')
    def corporate_debt_securities(self, request: Request) -> Response:
        """非金融企业：债券和贷款负债水平 - GET /api/fred-us/corporate-debt-securities/"""
        return self._get_specific_indicator('BCNSDODNS', request)
    
    @action(detail=False, methods=['get'], url_path='corporate-debt-equity-ratio')
    def corporate_debt_equity_ratio(self, request: Request) -> Response:
        """非金融企业债务占股权市值比例 - GET /api/fred-us/corporate-debt-equity-ratio/"""
        return self._get_specific_indicator('NCBCMDPMVCE', request)


class EmploymentIndicatorsMixin:
    """就业相关指标"""
    
    @action(detail=False, methods=['get'], url_path='unemployment')
    def unemployment_rate(self, request: Request) -> Response:
        """失业率 - GET /api/fred-us/unemployment/"""
        return self._get_specific_indicator('UNRATE', request)

    @action(detail=False, methods=['get'], url_path='unemployment-rate')
    def unemployment_rate_employment(self, request: Request) -> Response:
        """失业率 - GET /api/fred-us/unemployment-rate/"""
        return self._get_specific_indicator('UNRATE', request)

    @action(detail=False, methods=['get'], url_path='labor-force-participation')
    def labor_force_participation_rate(self, request: Request) -> Response:
        """劳动力参与率 - GET /api/fred-us/labor-force-participation/"""
        return self._get_specific_indicator('CIVPART', request)

    @action(detail=False, methods=['get'], url_path='job-openings')
    def job_openings_total(self, request: Request) -> Response:
        """职位空缺总数 - GET /api/fred-us/job-openings/"""
        return self._get_specific_indicator('JTSJOL', request)

    @action(detail=False, methods=['get'], url_path='quits-rate')
    def quits_rate_total(self, request: Request) -> Response:
        """辞职率 - GET /api/fred-us/quits-rate/"""
        return self._get_specific_indicator('JTSQUR', request)

    @action(detail=False, methods=['get'], url_path='initial-jobless-claims')
    def initial_jobless_claims(self, request: Request) -> Response:
        """首次申请失业救济人数 - GET /api/fred-us/initial-jobless-claims/"""
        return self._get_specific_indicator('ICSA', request)

    @action(detail=False, methods=['get'], url_path='employment-cost-index')
    def employment_cost_index(self, request: Request) -> Response:
        """就业成本指数 - GET /api/fred-us/employment-cost-index/"""
        return self._get_specific_indicator('ECIWAG', request)

    @action(detail=False, methods=['get'], url_path='nonfarm-payroll')
    def nonfarm_payroll_growth(self, request: Request) -> Response:
        """非农就业人数 - GET /api/fred-us/nonfarm-payroll/"""
        return self._get_specific_indicator('PAYEMS', request)

    @action(detail=False, methods=['get'], url_path='average-hourly-earnings')
    def average_hourly_earnings_growth(self, request: Request) -> Response:
        """平均时薪增长 - GET /api/fred-us/average-hourly-earnings/"""
        return self._get_specific_indicator('AHETPI', request)

    @action(detail=False, methods=['get'], url_path='population-55-over')
    def population_55_over(self, request: Request) -> Response:
        """55岁及以上人口 - GET /api/fred-us/population-55-over/"""
        return self._get_specific_indicator('LNU00024230', request)


class BankingIndicatorsMixin:
    """银行业相关指标"""
    
    @action(detail=False, methods=['get'], url_path='banking-federal-funds-rate')
    def banking_federal_funds_rate(self, request: Request) -> Response:
        """联邦基金利率 (Banking) - GET /api/fred-us/banking-federal-funds-rate/"""
        return self._get_specific_indicator('FEDFUNDS', request)
    
    @action(detail=False, methods=['get'], url_path='banking-reserve-balances-interest')
    def banking_reserve_balances_interest(self, request: Request) -> Response:
        """准备金余额利率 - GET /api/fred-us/banking-reserve-balances-interest/"""
        return self._get_specific_indicator('IORB', request)
    
    @action(detail=False, methods=['get'], url_path='banking-total-reserves')
    def banking_total_reserves(self, request: Request) -> Response:
        """总准备金余额 - GET /api/fred-us/banking-total-reserves/"""
        return self._get_specific_indicator('TOTRESNS', request)
    
    @action(detail=False, methods=['get'], url_path='banking-fed-balance-sheet')
    def banking_fed_balance_sheet(self, request: Request) -> Response:
        """美联储资产负债表总资产 - GET /api/fred-us/banking-fed-balance-sheet/"""
        return self._get_specific_indicator('WALCL', request)
    
    @action(detail=False, methods=['get'], url_path='banking-pce-inflation')
    def banking_pce_inflation(self, request: Request) -> Response:
        """PCE价格指数 (Banking) - GET /api/fred-us/banking-pce-inflation/"""
        return self._get_specific_indicator('PCEPI', request)
    
    @action(detail=False, methods=['get'], url_path='banking-unemployment-rate')
    def banking_unemployment_rate(self, request: Request) -> Response:
        """失业率 (Banking) - GET /api/fred-us/banking-unemployment-rate/"""
        return self._get_specific_indicator('UNRATE', request)
    
    @action(detail=False, methods=['get'], url_path='banking-commercial-loans')
    def banking_commercial_loans(self, request: Request) -> Response:
        """商业银行贷款和租赁 - GET /api/fred-us/banking-commercial-loans/"""
        return self._get_specific_indicator('TOTLL', request)
    
    @action(detail=False, methods=['get'], url_path='banking-prime-rate')
    def banking_prime_rate(self, request: Request) -> Response:
        """银行基准贷款利率 - GET /api/fred-us/banking-prime-rate/"""
        return self._get_specific_indicator('DPRIME', request)
    
    @action(detail=False, methods=['get'], url_path='aaa-corporate-bond-yield')
    def aaa_corporate_bond_yield(self, request: Request) -> Response:
        """穆迪Aaa级企业债券收益率 - GET /api/fred-us/aaa-corporate-bond-yield/"""
        return self._get_specific_indicator('AAA', request)
    
    @action(detail=False, methods=['get'], url_path='baa-corporate-bond-yield')
    def baa_corporate_bond_yield(self, request: Request) -> Response:
        """穆迪Baa级企业债券收益率 - GET /api/fred-us/baa-corporate-bond-yield/"""
        return self._get_specific_indicator('BAA', request)
    
    @action(detail=False, methods=['get'], url_path='high-yield-bond-spread')
    def high_yield_bond_spread(self, request: Request) -> Response:
        """高收益债券利差 - GET /api/fred-us/high-yield-bond-spread/"""
        return self._get_specific_indicator('BAMLH0A0HYM2', request)
    
    @action(detail=False, methods=['get'], url_path='primary-credit-loans')
    def primary_credit_loans(self, request: Request) -> Response:
        """主要信贷贷款 - GET /api/fred-us/primary-credit-loans/"""
        return self._get_specific_indicator('WPC', request)


class InflationIndicatorsMixin:
    """通胀相关指标"""
    
    @action(detail=False, methods=['get'], url_path='cpi')
    def consumer_price_index(self, request: Request) -> Response:
        """消费者价格指数 - GET /api/fred-us/cpi/"""
        return self._get_specific_indicator('CPIAUCSL', request)
    
    @action(detail=False, methods=['get'], url_path='pce-price-index')
    def pce_price_index(self, request: Request) -> Response:
        """PCE价格指数 - GET /api/fred-us/pce-price-index/"""
        return self._get_specific_indicator('PCEPI', request)
    
    @action(detail=False, methods=['get'], url_path='inflation-consumer-price-index')
    def inflation_consumer_price_index(self, request: Request) -> Response:
        """消费者价格指数 (CPI) - GET /api/fred-us/inflation-consumer-price-index/"""
        return self._get_specific_indicator('CPIAUCSL', request)
    
    @action(detail=False, methods=['get'], url_path='inflation-core-pce-price-index')
    def inflation_core_pce_price_index(self, request: Request) -> Response:
        """核心PCE价格指数 - GET /api/fred-us/inflation-core-pce-price-index/"""
        return self._get_specific_indicator('PCEPILFE', request)
    
    @action(detail=False, methods=['get'], url_path='inflation-federal-funds-rate')
    def inflation_federal_funds_rate(self, request: Request) -> Response:
        """联邦基金利率 (Inflation) - GET /api/fred-us/inflation-federal-funds-rate/"""
        return self._get_specific_indicator('FEDFUNDS', request)
    
    @action(detail=False, methods=['get'], url_path='inflation-unemployment-rate')
    def inflation_unemployment_rate(self, request: Request) -> Response:
        """失业率 (Inflation) - GET /api/fred-us/inflation-unemployment-rate/"""
        return self._get_specific_indicator('UNRATE', request)
    
    @action(detail=False, methods=['get'], url_path='inflation-retail-sales')
    def inflation_retail_sales(self, request: Request) -> Response:
        """零售销售 - GET /api/fred-us/inflation-retail-sales/"""
        return self._get_specific_indicator('RSAFS', request)
    
    @action(detail=False, methods=['get'], url_path='inflation-producer-price-index')
    def inflation_producer_price_index(self, request: Request) -> Response:
        """生产者价格指数 - GET /api/fred-us/inflation-producer-price-index/"""
        return self._get_specific_indicator('PPIACO', request)
    
    @action(detail=False, methods=['get'], url_path='inflation-breakeven-rate')
    def inflation_breakeven_rate(self, request: Request) -> Response:
        """10年盈亏平衡通胀率 - GET /api/fred-us/inflation-breakeven-rate/"""
        return self._get_specific_indicator('T10YIEM', request)
    
    @action(detail=False, methods=['get'], url_path='inflation-oil-prices')
    def inflation_oil_prices(self, request: Request) -> Response:
        """原油价格 (WTI) - GET /api/fred-us/inflation-oil-prices/"""
        return self._get_specific_indicator('DCOILWTICO', request)
    
    @action(detail=False, methods=['get'], url_path='consumer-price-inflation')
    def consumer_price_inflation(self, request: Request) -> Response:
        """消费者价格通胀率 - GET /api/fred-us/consumer-price-inflation/"""
        return self._get_specific_indicator('FPCPITOTLZGUSA', request)
    
    @action(detail=False, methods=['get'], url_path='nber-recession-indicator')
    def nber_recession_indicator(self, request: Request) -> Response:
        """NBER经济衰退指标 - GET /api/fred-us/nber-recession-indicator/"""
        return self._get_specific_indicator('USREC', request)


class TradeIndicatorsMixin:
    """贸易和国际收支相关指标"""
    
    @action(detail=False, methods=['get'], url_path='trade-balance-goods-services')
    def trade_balance_goods_services(self, request: Request) -> Response:
        """贸易平衡 - GET /api/fred-us/trade-balance-goods-services/"""
        return self._get_specific_indicator('BOPGSTB', request)

    @action(detail=False, methods=['get'], url_path='current-account-balance')
    def current_account_balance(self, request: Request) -> Response:
        """经常账户余额 - GET /api/fred-us/current-account-balance/"""
        return self._get_specific_indicator('IEABC', request)

    @action(detail=False, methods=['get'], url_path='foreign-treasury-holdings')
    def foreign_treasury_holdings(self, request: Request) -> Response:
        """外国持有的美国国债 - GET /api/fred-us/foreign-treasury-holdings/"""
        return self._get_specific_indicator('BOGZ1FL263061130Q', request)

    @action(detail=False, methods=['get'], url_path='customs-duties')
    def customs_duties(self, request: Request) -> Response:
        """关税收入 - GET /api/fred-us/customs-duties/"""
        return self._get_specific_indicator('B235RC1Q027SBEA', request)

    @action(detail=False, methods=['get'], url_path='federal-surplus-deficit-mts')
    def federal_surplus_deficit_mts(self, request: Request) -> Response:
        """财政盈余/赤字 - GET /api/fred-us/federal-surplus-deficit-mts/"""
        return self._get_specific_indicator('MTSDS133FMS', request)

    @action(detail=False, methods=['get'], url_path='net-exports')
    def net_exports(self, request: Request) -> Response:
        """净出口 - GET /api/fred-us/net-exports/"""
        return self._get_specific_indicator('NETEXP', request)

    @action(detail=False, methods=['get'], url_path='real-imports')
    def real_imports(self, request: Request) -> Response:
        """实际进口 - GET /api/fred-us/real-imports/"""
        return self._get_specific_indicator('IMPGSC1', request)

    @action(detail=False, methods=['get'], url_path='real-exports')
    def real_exports(self, request: Request) -> Response:
        """实际出口 - GET /api/fred-us/real-exports/"""
        return self._get_specific_indicator('EXPGSC1', request)


class HousingTreasuryIndicatorsMixin:
    """房地产和国债相关指标"""
    
    @action(detail=False, methods=['get'], url_path='housing')
    def housing_starts(self, request: Request) -> Response:
        """房屋开工数 - GET /api/fred-us/housing/"""
        return self._get_specific_indicator('HOUST', request)
    
    @action(detail=False, methods=['get'], url_path='mortgage-30y')
    def mortgage_30y_rate(self, request: Request) -> Response:
        """30年固定抵押贷款利率 - GET /api/fred-us/mortgage-30y/"""
        return self._get_specific_indicator('MORTGAGE30US', request)

    @action(detail=False, methods=['get'], url_path='treasury-10y')
    def treasury_10y_rate(self, request: Request) -> Response:
        """10年期国债利率 - GET /api/fred-us/treasury-10y/"""
        return self._get_specific_indicator('DGS10', request)

    @action(detail=False, methods=['get'], url_path='treasury-2y')
    def treasury_2y_rate(self, request: Request) -> Response:
        """2年期国债利率 - GET /api/fred-us/treasury-2y/"""
        return self._get_specific_indicator('DGS2', request)

    @action(detail=False, methods=['get'], url_path='treasury-3m')
    def treasury_3m_rate(self, request: Request) -> Response:
        """3个月国债利率 - GET /api/fred-us/treasury-3m/"""
        return self._get_specific_indicator('TB3MS', request)


__all__ = [
    'MonetaryIndicatorsMixin',
    'DebtIndicatorsMixin',
    'EmploymentIndicatorsMixin',
    'BankingIndicatorsMixin',
    'InflationIndicatorsMixin',
    'TradeIndicatorsMixin',
    'HousingTreasuryIndicatorsMixin',
]

