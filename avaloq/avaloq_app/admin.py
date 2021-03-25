from django.contrib import admin
from avaloq_app.models import Candidate, Question, Code_Entry, CodeTemplate
from django.contrib.auth.admin import UserAdmin




admin.site.register(CodeTemplate)
admin.site.register(Code_Entry)
admin.site.register(Candidate)


admin.site.register(Question)



# Register your models here.
