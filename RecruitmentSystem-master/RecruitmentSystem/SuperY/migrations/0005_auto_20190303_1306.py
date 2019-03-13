# Generated by Django 2.1.7 on 2019-03-03 05:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('SuperY', '0004_auto_20190302_2235'),
    ]

    operations = [
        migrations.CreateModel(
            name='ApplicantSearch',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('search_word', models.CharField(help_text='搜索关键词', max_length=255)),
                ('search_datetime', models.DateTimeField(auto_now_add=True, help_text='搜索时间')),
            ],
            options={
                'db_table': 'applicant_search',
                'ordering': ['search_datetime'],
            },
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('post_name', models.CharField(help_text='职位名称', max_length=255)),
                ('salary', models.CharField(help_text='薪资', max_length=255)),
                ('work_place', models.CharField(help_text='工作地点', max_length=255)),
                ('experience_require', models.CharField(help_text='工作经验要求', max_length=255)),
                ('graduate_require', models.CharField(help_text='毕业院校要求', max_length=255)),
                ('recruit_number', models.CharField(help_text='招聘人数', max_length=255)),
                ('post_info', models.TextField(help_text='岗位介绍')),
                ('publish_datetime', models.DateTimeField(auto_now=True, help_text='发布时间')),
            ],
            options={
                'db_table': 'post',
                'ordering': ['publish_datetime'],
            },
        ),
        migrations.CreateModel(
            name='PostTag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tag_name', models.CharField(help_text='标签名称', max_length=255)),
                ('post', models.ForeignKey(help_text='所属岗位', on_delete=django.db.models.deletion.CASCADE, to='SuperY.Post')),
            ],
            options={
                'db_table': 'post_tag',
            },
        ),
        migrations.AddField(
            model_name='company',
            name='company_info',
            field=models.TextField(null=True),
        ),
        migrations.AlterField(
            model_name='applicant',
            name='person_name',
            field=models.CharField(help_text='注册人姓名', max_length=255),
        ),
        migrations.AlterField(
            model_name='company',
            name='company_name',
            field=models.CharField(help_text='公司名称', max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='company',
            name='mail',
            field=models.CharField(help_text='电子邮箱', max_length=255),
        ),
        migrations.AlterField(
            model_name='company',
            name='passwd',
            field=models.CharField(help_text='密码', max_length=255),
        ),
        migrations.AlterField(
            model_name='company',
            name='person_name',
            field=models.CharField(help_text='注册人姓名', max_length=255),
        ),
        migrations.AlterField(
            model_name='company',
            name='phone_number',
            field=models.CharField(help_text='手机号码', max_length=255),
        ),
        migrations.AlterField(
            model_name='company',
            name='register_datetime',
            field=models.DateTimeField(auto_now_add=True, help_text='注册时间'),
        ),
        migrations.AddField(
            model_name='post',
            name='company',
            field=models.ForeignKey(help_text='所属公司', on_delete=django.db.models.deletion.CASCADE, to='SuperY.Company'),
        ),
        migrations.AddField(
            model_name='applicantsearch',
            name='applicant',
            field=models.ForeignKey(help_text='搜索人', on_delete=django.db.models.deletion.CASCADE, to='SuperY.Applicant'),
        ),
    ]
