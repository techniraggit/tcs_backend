from core.serializers import BaseSerializer, serializers
from doctor.models import *
from accounts.serializers import UserSerializer


class DoctorAvailabilitySerializer(BaseSerializer):
    class Meta:
        model = DoctorAvailability
        fields = ("id", "start_working_hr", "end_working_hr", "working_days")


class DoctorSerializer(BaseSerializer):
    doctor_availability = DoctorAvailabilitySerializer(many=True, read_only=True)
    user = UserSerializer(
        fields=[
            "id",
            "first_name",
            "last_name",
            "profile_image",
            "email",
            "phone_number",
            "is_active",
            "created",
        ]
    )

    class Meta:
        model = Doctors
        fields = [
            "user",
            "specialization",
            "medical_license",
            "education",
            "clinic_name",
            "clinic_address",
            "clinic_contact_no",
            "priority",
            "summary",
            "appointment_charges",
            "salary",
            "is_active",
            "doctor_availability",
        ]


class UsersSerializer(BaseSerializer):
    class Meta:
        model = Users
        fields = "__all__"


class PatientsSerializer(BaseSerializer):
    user = UsersSerializer()
    age = serializers.SerializerMethodField()

    class Meta:
        model = Patients
        fields = "__all__"

    def get_age(self, obj):
        return obj.age()


class AppointmentsSerializer(BaseSerializer):
    patient = PatientsSerializer(read_only=True)
    doctor = DoctorSerializer()

    class Meta:
        model = Appointments
        # fields = "__all__"
        exclude = ("previous_status",)


class AvailabilitySerializer(BaseSerializer):
    class Meta:
        model = Availability
        fields = "__all__"


class ConsultationSerializer(BaseSerializer):
    appointment = AppointmentsSerializer(read_only=True, fields=[
        "appointment_id",
        "schedule_date",
        "status", 
        "pre_health_issue",
        "pre_health_issue_text",
        "treatment_undergoing",
        "treatment_undergoing_text",
        "treatment_allergies",
        "treatment_allergies_text",
        "additional_note"
        ]
    )

    class Meta:
        model = Consultation
        fields = "__all__"
