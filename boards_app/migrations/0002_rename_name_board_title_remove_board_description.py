from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('boards_app', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='board',
            old_name='name',
            new_name='title',
        ),
        migrations.RemoveField(
            model_name='board',
            name='description',
        ),
    ]
