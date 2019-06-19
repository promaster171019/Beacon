from django.contrib import admin
from .models import Pdf, Timeline, BreakTime, DiscontinuationForm, UpgradeForm


admin.site.register(Pdf)
admin.site.register(Timeline)
admin.site.register(BreakTime)
admin.site.register(DiscontinuationForm)
admin.site.register(UpgradeForm)
