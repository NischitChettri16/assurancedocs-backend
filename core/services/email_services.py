from django.conf import settings

from django.core.mail import (
    EmailMultiAlternatives
)

from django.template.loader import (
    render_to_string
)


class EmailService:

    @staticmethod
    def send_otp_email(
        email,
        otp
    ):

        subject = (
            "AssuranceDocs AI - OTP Verification"
        )

        html_content = render_to_string(
            "emails/otp_email.html",
            {
                "otp": otp
            }
        )

        message = (
            EmailMultiAlternatives(
                subject=subject,
                body=f"Your OTP is {otp}",
                from_email=settings.EMAIL_HOST_USER,
                to=[email],
            )
        )

        message.attach_alternative(
            html_content,
            "text/html"
        )

        message.send()
    
    @staticmethod
    def send_hr_invitation(
    email,
    password,
    company
):

       subject = (
           "AssuranceDocs AI HR Account"
       )
   
       html_content = f"""
       <h2>Welcome to AssuranceDocs AI</h2>
   
       <p>
           Your company
           <strong>{company}</strong>
           has created an account for you.
       </p>
   
       <p>
           Email: {email}
       </p>
   
       <p>
           Temporary Password:
           <strong>{password}</strong>
       </p>
   
       <p>
           Please login and change your password.
       </p>
       """
   
       message = EmailMultiAlternatives(
           subject=subject,
           body=html_content,
           from_email=settings.DEFAULT_FROM_EMAIL,
           to=[email]
       )
   
       message.attach_alternative(
           html_content,
           "text/html"
       )

       message.send()