from django.db import models


class BotUser(models.Model):
    """
    Model representing a user of the bot.
    """
    user_id = models.CharField(max_length=255)
    full_name = models.CharField(max_length=300, null=True, blank=True)
    username = models.CharField(max_length=300, null=True, blank=True)
    language_code = models.CharField(max_length=10, null=True, blank=True, default='uz')
    is_blocked = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"User: {self.user_id} - {self.full_name} - {self.username}"

    @classmethod
    def get_admins(cls):
        """
        Returns a queryset of admin users.
        """
        return cls.objects.filter(is_admin=True)


class Vacancy(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    requirements = models.TextField(null=True, blank=True)
    salary = models.CharField(max_length=255, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
    @classmethod
    def active_vacancies(cls):
        """
        Returns a queryset of active vacancies.
        """
        return cls.objects.filter(is_active=True)



class Application(models.Model):
    """
    Model representing an application submitted by a user.
    """
    user = models.ForeignKey(BotUser, on_delete=models.CASCADE, related_name='applications')
    name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20)
    age = models.IntegerField(null=True, blank=True)
    vacancy = models.ForeignKey(Vacancy, on_delete=models.SET_NULL, related_name='applications', null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    portfolio = models.CharField(max_length=255, null=True, blank=True)
    portfolio_type = models.CharField(max_length=255, default='link')
    about = models.TextField(null=True, blank=True)
    status_choices = [
        ('new', 'Yangi'),
        ('in_task', 'Vazifa bajarmoqda'),
        ('task_completed', 'Vazifa bajarildi'),
        ('approved', 'Tasdiqlandi'),
        ('rejected', 'Bekor qilindi'),
    ]
    status = models.CharField(max_length=50, choices=status_choices, default='new')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Application: {self.name} - {self.status}"
    

class TechnicalTask(models.Model):
    """
    Model representing a technical task for a vacancy.
    """
    vacancy = models.ForeignKey(Vacancy, on_delete=models.SET_NULL, null=True, blank=True, related_name='technical_tasks')
    task = models.TextField()
    deadline = models.IntegerField(default=0) # in hours
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Technical Task for {self.vacancy.name} - Deadline: {self.deadline}"


class UserTask(models.Model):
    """
    Model representing a user's task submission.
    """
    user = models.ForeignKey(BotUser, on_delete=models.CASCADE, related_name='user_tasks')
    task = models.ForeignKey(TechnicalTask, on_delete=models.CASCADE, related_name='user_tasks')
    submission = models.TextField(null=True, blank=True)
    submission_type = models.CharField(max_length=255, default='link')
    status_choices = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('reviewing', 'Reviewing'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    status = models.CharField(max_length=50, choices=status_choices, default='pending')
    feedback = models.TextField(null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    deadline = models.DateTimeField(null=True, blank=True)
    user_deadline = models.CharField(max_length=255, null=True, blank=True) # user tanlagan muddat
    finished_at = models.DateTimeField(null=True, blank=True)
    checked_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Task Submission by {self.user.full_name} for {self.task.vacancy.name}"