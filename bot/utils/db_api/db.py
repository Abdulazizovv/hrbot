from asgiref.sync import sync_to_async

from botapp.models import BotUser, Vacancy, Application, TechnicalTask, UserTask
import logging
from django.utils import timezone
from datetime import timedelta

class Database:
    """
    A class to interact with the database.
    """

    @staticmethod
    @sync_to_async
    def get_or_create_user(user_id: str, full_name: str = None, username: str = None, language_code: str = 'uz'):
        """
        Get or create a user in the database.
        """
        user, created = BotUser.objects.get_or_create(
            user_id=user_id,
            defaults={
                'full_name': full_name,
                'username': username,
                'language_code': language_code
            }
        )
        return {
            'id': user.id,
            'user_id': user.user_id,
            'full_name': user.full_name,
            'username': user.username,
            'language_code': user.language_code,
            'is_blocked': user.is_blocked,
            'is_admin': user.is_admin
        }, created
    
    @staticmethod
    @sync_to_async
    def get_active_vacancies():
        """
        Get all active vacancies from the database.
        """
        vacanies = Vacancy.active_vacancies()
        
        if not vacanies:
            return None

        if vacanies:
            return [
                {
                    'id': vacancy.id,
                    'name': vacancy.name,
                    'description': vacancy.description,
                    'requirements': vacancy.requirements,
                    'salary': vacancy.salary
                }
                for vacancy in vacanies
            ]
    
    @staticmethod
    @sync_to_async
    def save_application_partially(user_id: str, part, data):
        """
        Save the application partially in the database.
        """
        try:
            user = BotUser.objects.get(user_id=user_id)
            application = Application.objects.filter(user=user, status='new').first()
            if not application:
                application = Application.objects.create(user=user, status='new')
                logging.info(f"New application created for user {user_id}.")
            
            if part == 'vacancy':
                vacancy = Vacancy.objects.filter(name=data).first()
                if not vacancy:
                    logging.error(f"Vacancy with name {data} does not exist.")
                    return None
                application.vacancy = vacancy
                application.save()
                return application.id
            setattr(application, part, data)
            application.save()
            return application.id
        except BotUser.DoesNotExist:
            logging.error(f"User with ID {user_id} does not exist.")
            return None
    
    @staticmethod
    @sync_to_async
    def update_application(user_id: str, field: str, value, status: str = 'sent'):
        """
        Update a field in the application.
        """
        try:
            user = BotUser.objects.get(user_id=user_id)
            application = Application.objects.filter(user=user, status=status).first()
            if not application:
                logging.error(f"Application for user {user_id} does not exist.")
                return None
            setattr(application, field, value)
            application.save()
            return {
                'id': application.id,
                'user': application.user.user_id,
                'name': application.name,
                'phone_number': application.phone_number,
                'age': application.age,
                'vacancy': application.vacancy.name if application.vacancy else None,
                'email': application.email,
                'portfolio': application.portfolio,
                'portfolio_type': application.portfolio_type,
                'about': application.about,
                'status': application.status
            }
        except BotUser.DoesNotExist:
            logging.error(f"User with ID {user_id} does not exist.")
            return None
    

    @staticmethod
    @sync_to_async
    def get_technical_task_for_vacancy(vacany_name):
        """
        Get the technical task for a specific vacancy.
        """
        try:
            vacancy = Vacancy.objects.filter(name=vacany_name).first()
            if not vacancy:
                logging.error(f"Vacancy with name {vacany_name} does not exist.")
                return None
            task = TechnicalTask.objects.filter(vacancy=vacancy).first()
            if task:
                return {
                    'id': task.id,
                    'task': task.task,
                    'deadline': task.deadline,
                    'vacancy': task.vacancy.name
                }
            return None
        except Vacancy.DoesNotExist:
            logging.error(f"Vacancy with {vacany_name} does not exist.")
            return None
        
    @staticmethod
    @sync_to_async
    def get_or_create_user_task(user_id: str, task_id: str):
        """
        Get or create a user task in the database.
        """
        try:
            user = BotUser.objects.get(user_id=user_id)
            task = TechnicalTask.objects.get(id=task_id)
            user_task, created = UserTask.objects.get_or_create(
                user=user,
                task=task,
                status='pending',
                defaults={
                    'deadline': timezone.localtime() + timedelta(hours=task.deadline),
                }
            )

            if created:
                # Only save if it was just created
                user_task.save()

            return {
                'id': user_task.id,
                'user': user_task.user.user_id,
                'task': user_task.task.task,
                'deadline': user_task.deadline.strftime('%Y-%m-%d %H:%M:%S') if user_task.deadline else None,
                'status': user_task.status,
                'created_at': user_task.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'updated_at': user_task.updated_at.strftime('%Y-%m-%d %H:%M:%S')
            }, created

        except (BotUser.DoesNotExist, TechnicalTask.DoesNotExist) as e:
            logging.error(f"Error getting or creating user task: {e}")
            return None, False
    
    @staticmethod
    @sync_to_async
    def have_application(user_id: str):
        """
        Check if the user has an application.
        """
        try:
            user = BotUser.objects.get(user_id=user_id)
            application = Application.objects.filter(user=user, status='new').first()
            return application is not None
        except BotUser.DoesNotExist:
            logging.error(f"User with ID {user_id} does not exist.")
            return False
    
    @staticmethod
    @sync_to_async
    def get_user_task(user_id: str):
        """
        Get a user task from the database.
        """
        try:
            user = BotUser.objects.get(user_id=user_id)
            user_task = UserTask.objects.filter(user=user, status__in=["pending", "sent"]).first()
            if user_task:
                return {
                    'id': user_task.id,
                    'user': user_task.user.user_id,
                    'task': user_task.task.task,
                    'deadline': user_task.deadline.strftime('%Y-%m-%d %H:%M:%S') if user_task.deadline else None,
                    'status': user_task.status,
                    'created_at': user_task.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    'updated_at': user_task.updated_at.strftime('%Y-%m-%d %H:%M:%S')
                }
            return None
        except (BotUser.DoesNotExist) as e:
            logging.error(f"Error getting user task: {e}")
            return None

    @staticmethod
    @sync_to_async
    def get_admins_id():
        """
        Get all admin user IDs from the database.
        """
        try:
            admins = BotUser.objects.filter(is_admin=True)
            return [admin.user_id for admin in admins]
        except Exception as e:
            logging.error(f"Error getting admins: {e}")
            return []
    
    @staticmethod
    @sync_to_async
    def get_application_by_id(application_id: str):
        """
        Get an application by its ID.
        """
        try:
            application = Application.objects.get(id=application_id)
            return {
                'id': application.id,
                'user': application.user.user_id,
                'name': application.name,
                'phone_number': application.phone_number,
                'age': application.age,
                'vacancy': application.vacancy.name if application.vacancy else None,
                'email': application.email,
                'portfolio': application.portfolio,
                'portfolio_type': application.portfolio_type,
                'about': application.about,
                'status': application.status
            }
        except Application.DoesNotExist:
            logging.error(f"Application with ID {application_id} does not exist.")
            return None
    
    @staticmethod
    @sync_to_async
    def get_users_progress_tasks():
        """
        Get all user tasks from the database.
        """
        try:
            tasks = UserTask.objects.filter(status__in=["pending"])
            return [
                {
                    'id': task.id,
                    'user': task.user.user_id,
                    'task': task.task.task,
                    'deadline': task.deadline.strftime('%Y-%m-%d %H:%M:%S') if task.deadline else None,
                    'status': task.status,
                    'created_at': task.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    'updated_at': task.updated_at.strftime('%Y-%m-%d %H:%M:%S')
                }
                for task in tasks
            ]
        except Exception as e:
            logging.error(f"Error getting user tasks: {e}")
            return []
        
    @staticmethod
    @sync_to_async
    def change_user_task_status(user_id: str, task_id: str, status: str):
        """
        Change the status of a user task.
        """
        try:
            user = BotUser.objects.get(user_id=user_id)
            task = TechnicalTask.objects.get(id=task_id)
            user_task = UserTask.objects.get(user=user, task=task)
            user_task.status = status
            user_task.save()
            return {
                'id': user_task.id,
                'user': user_task.user.user_id,
                'task': user_task.task.task,
                'deadline': user_task.deadline.strftime('%Y-%m-%d %H:%M:%S') if user_task.deadline else None,
                'status': user_task.status,
                'created_at': user_task.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'updated_at': user_task.updated_at.strftime('%Y-%m-%d %H:%M:%S')
            }
        except (BotUser.DoesNotExist, TechnicalTask.DoesNotExist, UserTask.DoesNotExist) as e:
            logging.error(f"Error changing user task status: {e}")
            return None
    
    @staticmethod
    @sync_to_async
    def get_user_task_by_id(task_id: str):
        """
        Get a user task by its ID.
        """
        try:
            user_task = UserTask.objects.get(id=task_id)
            return {
                'id': user_task.id,
                'user': user_task.user.user_id,
                'task': user_task.task.task,
                'vacancy': user_task.task.vacancy.id if user_task.task.vacancy else None,
                'deadline': user_task.deadline.strftime('%Y-%m-%d %H:%M:%S') if user_task.deadline else None,
                'status': user_task.status,
                'is_valid': timezone.localtime() < user_task.deadline if user_task.deadline else False,
                'created_at': user_task.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'updated_at': user_task.updated_at.strftime('%Y-%m-%d %H:%M:%S')
            }
        except UserTask.DoesNotExist:
            logging.error(f"User task with ID {task_id} does not exist.")
            return None
        
    @staticmethod
    @sync_to_async
    def add_submission(user_task_id, submission: str, submission_type: str='link'):
        """
        Add a submission to a user task.
        """
        try:
            user_task = UserTask.objects.get(id=user_task_id)
            user_task.submission = submission
            user_task.submission_type = submission_type
            user_task.status = 'sent'
            user_task.save()
            return {
                'id': user_task.id,
                'user': user_task.user.user_id,
                'task': user_task.task.task,
                'deadline': user_task.deadline.strftime('%Y-%m-%d %H:%M:%S') if user_task.deadline else None,
                'status': user_task.status,
                'created_at': user_task.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'updated_at': user_task.updated_at.strftime('%Y-%m-%d %H:%M:%S')
            }
        except (UserTask.DoesNotExist) as e:
            logging.error(f"Error adding submission: {e}")
            return None
        
    @staticmethod
    @sync_to_async
    def change_application_status(user_id: str, vacancy_id: str, status: str):
        """
        Change the status of an application.
        """
        try:
            user = BotUser.objects.get(user_id=user_id)
            vacancy = Vacancy.objects.get(id=vacancy_id)
            application = Application.objects.get(user=user, vacancy=vacancy)
            if not application:
                logging.error(f"Application for user {user_id} and vacancy {vacancy_id} does not exist.")
                return None
            application.status = status
            application.save()
            return {
                'id': application.id,
                'user': application.user.user_id,
                'name': application.name,
                'phone_number': application.phone_number,
                'age': application.age,
                'vacancy': application.vacancy.name if application.vacancy else None,
                'email': application.email,
                'portfolio': application.portfolio,
                'portfolio_type': application.portfolio_type,
                'about': application.about,
                'status': application.status
            }
        except Application.DoesNotExist:
            logging.error(f"Application with ID does not exist.")
            return None
    
    @staticmethod
    @sync_to_async
    def update_user_task(user_task_id, field, value):
        """
        Update a field in the user task.
        """
        try:
            user_task = UserTask.objects.get(id=user_task_id)
            setattr(user_task, field, value)
            user_task.save()
            return {
                'id': user_task.id,
                'user': user_task.user.user_id,
                'task': user_task.task.task,
                'deadline': user_task.deadline.strftime('%Y-%m-%d %H:%M:%S') if user_task.deadline else None,
                'status': user_task.status,
                'created_at': user_task.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'updated_at': user_task.updated_at.strftime('%Y-%m-%d %H:%M:%S')
            }
        except (UserTask.DoesNotExist) as e:
            logging.error(f"Error updating user task: {e}")
            return None