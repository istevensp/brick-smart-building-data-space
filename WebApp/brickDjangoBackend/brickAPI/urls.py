from django.urls import path
from . import views

urlpatterns = [
    path('sensors/', views.getAllSensors, name='sensors'),
    path('sensors/<str:sensor_id>', views.getSensorData, name='sensor_by_id'),
    path('sensors/history/<str:sensor_id>/<str:date_from>/<str:date_to>/<str:interval>', views.getSensorDataHistory, name='sensor_history_by_id'),
    path('equipment/<str:equipment_id>', views.getSensorsFromEquipment, name='sensors_by_equipment'),
    path('getAllSubClasses/<str:pClass>', views.getAllSubClasses, name='get_all_subclasses'),
    path('getClassProperties/<str:pClass>', views.getClassProperties, name='get_class_properties'),
    path('getInstances/<str:pClass>', views.getInstancesFromEspol, name='get_instances_from_espol'),
    path('insertData/', views.insertEntityToEspolSchema , name='insert_data_espol_schema'),
    path('deleteData/<str:entity>', views.deleteEntityFromEspolSchema, name='delete_data_espol_schema'),
]