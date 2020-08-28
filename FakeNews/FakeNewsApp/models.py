from django.db import models
from django.contrib.auth.models import User
from .storage import OverwriteStorage
from datetime import datetime
from string import digits
from random import choice
from statistics import mean 

User._meta.get_field('email')._unique = True

class Reader(models.Model):
    def user_directory_path_dp(instance, filename):
        return 'FakeNewsApp/Reader/{0}/{1}'.format('dp', str(instance.id.get_username()+str(datetime.now())))
    id = models.OneToOneField(User, on_delete=models.CASCADE,primary_key=True)
    fname = models.CharField(max_length=100, null=True)
    lname = models.CharField(max_length=100, null=True)
    dp = models.FileField(upload_to=user_directory_path_dp, null=True, storage=OverwriteStorage(), blank=True)
    def __str__(this):
        return (str(this.fname) +" "+ str(this.lname))


class Journalist(models.Model):
    def user_directory_path_dp(instance, filename):
        return 'FakeNewsApp/Journalist/{0}/{1}'.format('dp', str(instance.id.get_username()+str(datetime.now())))
    def user_directory_path_idproof(instance, filename):
        return 'FakeNewsApp/Journalist/{0}/{1}'.format('idproof', str(instance.id.get_username()+str(datetime.now())))
    id = models.OneToOneField(User, on_delete=models.CASCADE,primary_key=True)
    fname = models.CharField(max_length=100, null=True)
    lname = models.CharField(max_length=100, null=True)
    idproof = models.FileField(upload_to=user_directory_path_idproof,null=True, storage=OverwriteStorage())
    dp = models.FileField(upload_to=user_directory_path_dp,null=True, storage=OverwriteStorage(), blank=True)
    def __str__(this):
        return (str(this.fname) +" "+ str(this.lname))

    verified = models.BooleanField(default=False)
    verification_time = models.DateTimeField(null=True, blank=True)
    
    deactivation_time = models.DateTimeField(blank=True, null=True)
    deactivations = models.IntegerField(default=0)
    

    def deactivate(self):
        self.deactivations  = self.deactivations + 1
        self.deactivation_time = datetime.now()
        self.save()


    def is_activated(self):
        if self.verified:
            if self.deactivations == 0:
                return True
            elif self.deactivations == 1:
                if datetime.now() - self.deactivation_time >= datetime.timedelta(days = 7):
                    return True
                else:
                    return False
            else:
                return False
        else:
            return False
        


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__verified = self.verified
    
    def save(self, *args, **kwargs):
        if self.verified and not self.__verified:
            self.verification_time = datetime.now()
        elif not self.verified and self.__verified:
            self.verification_time = None
        super().save(*args, **kwargs)


class Auditor(models.Model):
    def user_directory_path_dp(instance, filename):
        return 'FakeNewsApp/Auditor/{0}/{1}'.format('dp', str(instance.id.get_username()+str(datetime.now())))
    def user_directory_path_idproof(instance, filename):
        return 'FakeNewsApp/Auditor/{0}/{1}'.format('idproof', str(instance.id.get_username()+str(datetime.now())))
    id = models.OneToOneField(User, on_delete=models.CASCADE,primary_key=True)
    fname = models.CharField(max_length=100, null=True)
    lname = models.CharField(max_length=100, null=True)
    dp = models.FileField(upload_to=user_directory_path_dp,null=True,blank=True, storage=OverwriteStorage())
    idproof = models.FileField(upload_to=user_directory_path_idproof,null=True, blank=True, storage=OverwriteStorage())
    verified = models.BooleanField(default=False)
    verification_time = models.DateTimeField(null=True, blank=True)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__verified = self.verified
    
    def save(self, *args, **kwargs):
        if self.verified and not self.__verified:
            self.verification_time = datetime.now()
        elif not self.verified and self.__verified:
            self.verification_time = None
        super().save(*args, **kwargs)



    def get_stake(self):
        try:
            stakeTrans = StakeTransaction.objects.filter(auditor=self)
            init = 0.0
            for a in stakeTrans:
                if a.tranType == '+':
                    init = init + a.amount
                elif a.tranType == '-':
                    init = init - a.amount
            return init
        except:
            return 0.0

    def __str__(this):
        return (str(this.fname) +" "+ str(this.lname))


def StringKeyGenerator(length=12, chars=digits):
    newid = [choice(chars) for i in range(length)]
    try:
        a = Article.objects.get(id=newid)
        return StringKeyGenerator(length=length, chars=chars)
    except:
        return "".join(newid);

class Article(models.Model):
    def article_directory_path(instance, filename):
        return 'FakeNewsApp/Article/{0}'.format( str(str(instance.id)+str(datetime.now())))
    
    id = models.CharField(primary_key=True, default=StringKeyGenerator, max_length=12)
    headline = models.CharField(max_length=1000)
    body = models.TextField()
    src = models.TextField()
    articleTypeChoices = [
        ("Sports", "Sports"),
        ("Politics", "Politics"),
        ("Regional", "Regional"),
        ("International", "International"),
        ("Crime", "Crime"),
        ("Technology", "Technology"),
        ("Other", "Other"),
    ]
    articleType = models.CharField(choices=articleTypeChoices, default="Other", max_length=13)
    img = models.FileField(upload_to=article_directory_path,null=True, storage=OverwriteStorage(), blank=True)
    journalist = models.ForeignKey(Journalist, on_delete=models.CASCADE)
    auditor = models.ForeignKey(Auditor, on_delete=models.CASCADE, null=True, blank=True)
    audit_requested = models.DateTimeField(null=True, blank=True)
    audit_completed = models.DateTimeField(default=None, null=True, blank=True)
    audit_status = models.BooleanField(default=False)
    post_time = models.DateTimeField(auto_now_add=True)
    block_time =  models.DateTimeField(null=True, blank=True)
    
    def get_likes(self):
        try:
            return len(Like.objects.filter(article=self))
        except:
            return 0


    def get_comments(self):
        try:
            return Comment.objects.filter(article=self).order_by('timestamp')
        except:
            return list()

    def __str__(this):
        return str(this.headline)


class StakeTransaction(models.Model):
    id = models.AutoField(primary_key=True)
    auditor = models.ForeignKey(Auditor, on_delete=models.CASCADE)
    amount = models.FloatField()
    tranType = models.CharField(max_length=1, choices=[('+', 'Add'), ('-', 'Remove')])
    timestamp = models.DateTimeField(auto_now_add=True)
    def __str__(this):
        return str(str(this.auditor.fname) + " "+ str(this.amount))


class Like(models.Model):
    reader = models.ForeignKey(Reader, on_delete=models.CASCADE)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)



class Comment(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    reader = models.ForeignKey(Reader, on_delete=models.CASCADE)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    comment = models.TextField()