from django.db import models


# Create your models here.

class Data(models.Model):
    avgIc = models.CharField(max_length=255)
    avgAbsIc = models.CharField(max_length=255)
    avgPositiveIc = models.CharField(max_length=255)
    positiveIcRatio = models.CharField(max_length=255)
    ir = models.CharField(max_length=255)
    tStatistic = models.CharField(max_length=255)
    gradingRankIC = models.CharField(max_length=255)
    avgTurnOverRate = models.CharField(max_length=255)
    medianTurnOverRate = models.CharField(max_length=255)
    excessCumReturn_benchMark = models.CharField(max_length=255)
    excessCumReturn_winAndLoss = models.CharField(max_length=255)
    excessAnnualReturn_benchMark = models.CharField(max_length=255)
    excessAnnualReturn_winAndLoss = models.CharField(max_length=255)


class Test(models.Model):
    # id = models.IntegerField(max_length=20)
    name = models.CharField(max_length=20)


class Reporter(models.Model):
    full_name = models.CharField(max_length=20)

    def __str__(self):
        return self.full_name


class Article(models.Model):
    pub_date = models.DateField
    headline = models.CharField(max_length=200)
    content = models.TextField
    reporter = models.ForeignKey(Reporter, on_delete=models.CASCADE)


class Contact(models.Model):
    name = models.CharField(max_length=200)
    age = models.IntegerField(default=0)
    email = models.EmailField()

    def __unicode__(self):
        return self.name


class Tag(models.Model):
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)

    def __unicode__(self):
        return self.name

# class Permission(models.Model):
#     # 权限表
#     title = models.CharField(verbose_name='标题',max_length=32)
#     url = models.CharField(verbose_name="含正则URL",max_length=64)
#     is_menu = models.BooleanField(verbose_name="是否是菜单")
#
#     class Meta:
#         verbose_name_plural = "权限表"
#
#     def __str__(self):
#         return self.title
#
# class User(models.Model):
#     # 用户表
#     username = models.CharField(verbose_name='用户名',max_length=32)
#     password = models.CharField(verbose_name='密码',max_length=64)
#     email = models.CharField(verbose_name='邮箱',max_length=32)
#
#     roles = models.ManyToManyField(verbose_name='具有的所有角色',to="Role",blank=True)
#     class Meta:
#         verbose_name_plural = "用户表"
#
#     def __str__(self):
#         return self.username
#
# class Role(models.Model):
#     # 角色表
#     title = models.CharField(max_length=32)
#     permissions = models.ManyToManyField(verbose_name='具有的所有权限',to='Permission',blank=True)
#     class Meta:
#         verbose_name_plural = "角色表"
#
#     def __str__(self):
#         return self.title
#
