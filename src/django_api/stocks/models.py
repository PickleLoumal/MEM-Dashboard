from django.db import models


class StockScore(models.Model):
    """Daily stock scoring snapshot stored alongside CSI300 company data."""

    calculation_date = models.DateField(help_text="Date of the score calculation")
    ticker = models.CharField(max_length=50, help_text="Stock ticker/symbol")
    company_name = models.CharField(max_length=255, help_text="Company name")
    buy_score = models.PositiveSmallIntegerField(default=0, help_text="Buy signal score (0-100)")
    buy_reasons = models.JSONField(default=list, blank=True, help_text="Triggered buy signal reasons")
    sell_score = models.PositiveSmallIntegerField(default=0, help_text="Sell signal score (0-100)")
    sell_reasons = models.JSONField(default=list, blank=True, help_text="Triggered sell signal reasons")
    total_score = models.DecimalField(max_digits=6, decimal_places=2, default=0, help_text="Unified score (-100 to +100)")
    score_components = models.JSONField(default=dict, blank=True, help_text="Component breakdown with raw/weighted contributions")
    last_close = models.DecimalField(max_digits=20, decimal_places=6, blank=True, null=True, help_text="Previous close price")
    last_trading_date = models.DateField(blank=True, null=True, help_text="Last trading date in the dataset")
    cmf_value = models.DecimalField(max_digits=12, decimal_places=6, blank=True, null=True, help_text="Latest CMF value")
    obv_value = models.BigIntegerField(blank=True, null=True, help_text="Latest OBV value")
    ma5 = models.DecimalField(max_digits=20, decimal_places=6, blank=True, null=True, help_text="MA5 value")
    ma10 = models.DecimalField(max_digits=20, decimal_places=6, blank=True, null=True, help_text="MA10 value")
    recommended_action = models.CharField(max_length=50, blank=True, help_text="Resulting recommended action")
    recommended_action_detail = models.TextField(blank=True, help_text="Detailed recommended action explanation")
    signal_date = models.DateField(blank=True, null=True, help_text="Signal generation date")
    execution_date = models.DateField(blank=True, null=True, help_text="Suggested execution date (typically T+1)")
    suggested_position_pct = models.DecimalField(max_digits=6, decimal_places=4, blank=True, null=True, help_text="Suggested position percentage (0-1)")
    stop_loss_price = models.DecimalField(max_digits=20, decimal_places=6, blank=True, null=True, help_text="Stop-loss trigger price")
    take_profit_price = models.DecimalField(max_digits=20, decimal_places=6, blank=True, null=True, help_text="Take-profit trigger price")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'stock_scores'
        verbose_name = "Stock Score"
        verbose_name_plural = "Stock Scores"
        unique_together = ('calculation_date', 'ticker')
        ordering = ('-calculation_date', 'ticker')

    def __str__(self):
        return f"{self.calculation_date} - {self.ticker}"


class ScoreCalculationLog(models.Model):
    """Tracking metadata around each daily scoring run."""

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    calculation_date = models.DateField(unique=True, help_text="Date of the scoring batch")
    start_time = models.DateTimeField(help_text="Start timestamp of the batch")
    end_time = models.DateTimeField(blank=True, null=True, help_text="End timestamp of the batch")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', help_text="Status of the batch")
    total_stocks = models.PositiveIntegerField(default=0, help_text="Number of stocks processed")
    successful_stocks = models.PositiveIntegerField(default=0, help_text="Number of successful stock updates")
    failed_stocks = models.PositiveIntegerField(default=0, help_text="Number of stocks that failed to process")
    processed_stocks = models.PositiveIntegerField(default=0, help_text="Number of stocks processed so far")
    current_stock = models.CharField(max_length=50, blank=True, help_text="Currently processing stock symbol")
    error_message = models.TextField(blank=True, help_text="Error message if the run failed")

    class Meta:
        db_table = 'score_calculation_logs'
        verbose_name = "Score Calculation Log"
        verbose_name_plural = "Score Calculation Logs"
        ordering = ('-calculation_date',)

    def __str__(self):
        return f"{self.calculation_date} - {self.status}"
