from django.db import models
from datetime import datetime
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager, Group, Permission
from web_base.settings import (FREE_USERS_VIDEO_DUR_MS, 
                               PAID_USERS_VIDEO_DUR_MS, 
                               FREE_USERS_STORAGE_MB, 
                               PAID_USERS_STORAGE_MB,
                               FREE_USERS_TIME_VIDEO_DUR_RESET_DAYS,
                               PAID_USERS_TIME_VIDEO_DUR_RESET_DAYS)
from picklefield.fields import PickledObjectField
from django.conf import settings
import os
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **options):
        users = UserBase.objects.all()
        for user in users:
            user.videos_time_used_sec = 0
            user.save()

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True')
        
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True')
        
        return self.create_user(email, password, **extra_fields)

class UserBase(AbstractBaseUser,PermissionsMixin):
    email = models.EmailField(max_length=255, unique=True)
    firstname = models.CharField(max_length=50)
    lastname = models.CharField(max_length=50)
    referral = models.CharField(max_length=200, null=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    is_free = models.BooleanField(default=True)
    storage_MB_used = models.FloatField(default=0)
    videos_time_used_ms = models.FloatField(default=0)
    videos_time_used_last_updated_date = models.DateTimeField(default=datetime.now)
    max_video_duration_ms = models.FloatField(default=FREE_USERS_VIDEO_DUR_MS)
    max_storage_capacity_MB = models.FloatField(default=FREE_USERS_STORAGE_MB)
   
    is_superuser = models.BooleanField(default=False)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['firstname', 'lastname']
    
    objects = UserManager()
    # groups = models.ManyToManyField(Group, related_name='user_base_set')
    # user_permissions = models.ManyToManyField(Permission, related_name='user_base_set')
    def __str__(self):
        return f'{self.firstname} {self.lastname}'
    class Meta:
        verbose_name = "User"

    def save(self, *args, **kwargs):
        if self.is_free:
            self.max_video_duration_ms = FREE_USERS_VIDEO_DUR_MS
            self.max_storage_capacity_MB = FREE_USERS_STORAGE_MB
        else:
            self.max_video_duration_ms = PAID_USERS_VIDEO_DUR_MS
            self.max_storage_capacity_MB = PAID_USERS_STORAGE_MB
        super().save(*args, **kwargs)

    def update_storage(self):
        translations = TranslationInfo_User.objects.filter(user=self, using_storage=True, to_show=True)
        ocupied_space = 0
        for tr in translations:
            ocupied_space += tr.update_storage()

        if abs(self.storage_MB_used - ocupied_space) < 0.5:
            # the same, no need to update the user
            return ocupied_space 
        
        self.storage_MB_used = ocupied_space
        print(f"Ocupied space for User {self} is {ocupied_space} MB.")
        self.save()
        return self.storage_MB_used
    
    # def update_time_used(self):
    #     translations = TranslationInfo_User.objects.filter(user=self, using_storage=True, to_show=True)
    #     time_used = 0
        

    def add_time_used(self, new_video_time_ms:float):
        if self.videos_time_used_ms < self.max_video_duration_ms:
            remaining_space = self.max_video_duration_ms - self.videos_time_used_ms

            if remaining_space >= new_video_time_ms:
                self.videos_time_used_ms += new_video_time_ms
                self.save()
                return True
        return False

    def reset_time_used(self):
        self.videos_time_used_ms = 0
        self.videos_time_used_last_updated_date = models.DateTimeField(default=datetime.now)
        self.save()

    def get_remaining_video_dur_reset_days(self):
        today = datetime.now()
        days_since_updated = today - self.videos_time_used_last_updated_date
        if self.is_free:
            print(FREE_USERS_TIME_VIDEO_DUR_RESET_DAYS - days_since_updated)
            return FREE_USERS_TIME_VIDEO_DUR_RESET_DAYS - days_since_updated
        else:
            print(PAID_USERS_TIME_VIDEO_DUR_RESET_DAYS - days_since_updated)
            return PAID_USERS_TIME_VIDEO_DUR_RESET_DAYS - days_since_updated

# @receiver(post_save, sender=UserBase)
# def update_user_limits(sender, instance:UserBase, *kwargs):
#     type = "Free " if instance.is_free else "Paid"
#     print(f"user {instance} saved to database. Updating limits.")
#     if instance.is_free:
#         instance.max_video_duration_ms = FREE_USERS_VIDEO_DUR_MS
#         instance.max_storage_capacity_MB = FREE_USERS_STORAGE_MB
#     else:
#         instance.max_video_duration_ms = PAID_USERS_VIDEO_DUR_MS
#         instance.max_storage_capacity_MB = PAID_USERS_STORAGE_MB
#     instance.save()

class TranslationInfo_User(models.Model):
    user = models.ForeignKey(to=UserBase, related_name="translations", on_delete=models.CASCADE)
    transl_name = models.CharField(max_length=200, default="Unknown")
    to_show = models.BooleanField(default=True)
    translation_info = PickledObjectField() # TranslationPack
    using_storage = models.BooleanField(default=False)
    storage_weight_MB = models.FloatField(default=0)
    date_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.user}. \n\n {self.translation_info}'
    
    def update_storage(self):
        source_video = self.translation_info.source_video#.get_filename()
        source_audio = self.translation_info.source_audio#.get_filename()
        transl_video = self.translation_info.translated_video#.get_filename()
        transl_audio = self.translation_info.translated_audio#.get_filename()
        ocupied_space = 0
        if source_video != None: 
            file_path = source_video.get_filename()
            if os.path.exists(file_path):
                file_stats = os.stat(file_path)
                ocupied_space += file_stats.st_size / (1024 * 1024)
        if source_audio != None: 
            file_path = source_audio.get_filename()
            if os.path.exists(file_path):
                file_stats = os.stat(file_path)
                ocupied_space += file_stats.st_size / (1024 * 1024)
        if transl_video != None: 
            file_path = transl_video.get_filename()
            if os.path.exists(file_path):
                file_stats = os.stat(file_path)
                ocupied_space += file_stats.st_size / (1024 * 1024)
        if transl_audio != None: 
            file_path = transl_audio.get_filename()
            if os.path.exists(file_path):
                file_stats = os.stat(file_path)
                ocupied_space += file_stats.st_size / (1024 * 1024)

        if abs(self.storage_weight_MB - ocupied_space) < 0.5:
            # the same, no need to update the user
            return ocupied_space
        
        self.storage_weight_MB = ocupied_space
        print(f"Ocupied space for Translation Info {self.pk} is {ocupied_space} MB.")
        self.save()
        return self.storage_weight_MB
    
    def user_delete(self):
        self.to_show = False
        source_video = self.translation_info.source_video#.get_filename()
        source_audio = self.translation_info.source_audio#.get_filename()
        transl_video = self.translation_info.translated_video#.get_filename()
        transl_audio = self.translation_info.translated_audio#.get_filename()
        try:
            os.remove(source_video.get_filename())
        except Exception as er:
            print(f"Error while removing translation info \"{self.transl_name}\": {er}")
        try:
            os.remove(source_audio.get_filename())
        except Exception as er:
            print(f"Error while removing translation info \"{self.transl_name}\": {er}")
        try:
            os.remove(transl_video.get_filename())
        except Exception as er:
            print(f"Error while removing translation info \"{self.transl_name}\": {er}")
        try:
            os.remove(transl_audio.get_filename())
        except Exception as er:
            print(f"Error while removing translation info \"{self.transl_name}\": {er}")
        
        self.save()


class Saved_voices_user(models.Model):
    user = models.ForeignKey(to=UserBase, related_name="cloned_voices", on_delete=models.CASCADE)
    voice_name = models.CharField(max_length=200)
    to_show = models.BooleanField(default=True)
    # language = models.CharField(max_length=50)
    voice_sample = PickledObjectField() # AudioSegment
    def __str__(self):
        return f'{self.user}. \t {self.voice_name}'
    
    def save(self, *args, **kwargs):
        if self.pk is None:
            # Check if the voice name already exists for the user
            if self.user.cloned_voices.filter(voice_name=self.voice_name, to_show=True).exists():

                raise Exception("A voice with this name already exists for this user.")
        super().save(*args, **kwargs)

    def user_delete(self):
        self.to_show = False
        self.voice_sample = []
        self.save()


# class EmailVerification(models.Model):
#     user = models.OneToOneField(
#         settings.AUTH_USER_MODEL,
#         on_delete=models.CASCADE,
#         related_query_name="verification"
#     )
#     verified = models.BooleanField(default=False)



