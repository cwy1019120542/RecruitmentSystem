from django.db import models

class Applicant(models.Model):
	phone_number=models.CharField(max_length=255,help_text='手机号码')
	mail=models.CharField(max_length=255,help_text='电子邮箱',null=True)
	person_name=models.CharField(max_length=255,help_text='注册人姓名')
	passwd=models.CharField(max_length=255,help_text='密码')
	head_pic=models.ImageField(upload_to='applicant',null=True)
	register_datetime=models.DateTimeField(auto_now_add=True,help_text='注册时间')
	class Meta:
		db_table='applicant'
		ordering=['register_datetime']
	def __str__(self):
		return self.phone_number+'['+self.person_name+']'

class Company(models.Model):
	phone_number=models.CharField(max_length=255,help_text='手机号码')
	mail=models.CharField(max_length=255,help_text='电子邮箱')
	person_name=models.CharField(max_length=255,help_text='注册人姓名')
	passwd=models.CharField(max_length=255,help_text='密码')
	business_licence=models.ImageField(upload_to='company',null=True,help_text='营业执照')
	company_name=models.CharField(max_length=255,help_text='公司名称',null=True)
	register_datetime=models.DateTimeField(auto_now_add=True,help_text='注册时间')
	is_check=models.BooleanField(default=False,help_text='是否验证')
	company_info=models.TextField(null=True,help_text='公司简介')
	company_type=models.CharField(null=True,max_length=255,help_text='公司类型')
	main_product=models.CharField(null=True,max_length=255,help_text='主营产品')
	staff_number=models.CharField(null=True,max_length=255,help_text='员工数')
	address=models.CharField(null=True,max_length=255,help_text='公司地址')
	class Meta:
		db_table='company'
		ordering=['register_datetime']
	def __str__(self):
		return self.company_name

class ApplicantSearch(models.Model):
	applicant=models.ForeignKey(Applicant,on_delete=models.CASCADE,help_text='搜索人')
	search_word=models.CharField(max_length=255,help_text='搜索关键词')
	search_datetime=models.DateTimeField(auto_now_add=True,help_text='搜索时间')
	class Meta:
		db_table='applicant_search'
		ordering=['search_datetime']
	def __str__(self):
		return self.search_word

class Resume(models.Model):
	applicant=models.OneToOneField(Applicant,on_delete=models.CASCADE,help_text='所属求职者')
	resume_name=models.CharField(max_length=255,help_text='简历名称',null=True)
	head_pic=models.ImageField(upload_to='resume',null=True)
	applicant_name=models.CharField(max_length=255,help_text='求职者名称',null=True)
	sex=models.CharField(max_length=255,help_text='性别',null=True)
	age=models.CharField(max_length=255,help_text='年龄',null=True)
	birth_place=models.CharField(max_length=255,help_text='出生地',null=True)
	experience=models.CharField(max_length=255,help_text='工作经验',null=True)
	phone_number=models.CharField(max_length=255,help_text='手机号',null=True)
	mail=models.CharField(max_length=255,help_text='邮箱',null=True)
	apply_status=models.CharField(max_length=255,help_text='求职状态',null=True)
	profession=models.CharField(max_length=255,help_text='期望行业',null=True)
	work_place=models.CharField(max_length=255,help_text='期望工作地点',null=True)
	post_name=models.CharField(max_length=255,help_text='期望职位',null=True)
	salary=models.CharField(max_length=255,help_text='期望薪资',null=True)
	work_nature=models.CharField(max_length=255,help_text='工作性质',null=True)
	self_judge=models.TextField(help_text='自我评价',null=True)
	update_datetime=models.DateTimeField(auto_now=True,help_text='更新时间')
	company_look=models.ManyToManyField(Company)
	class Meta:
		db_table='resume'
		ordering=['update_datetime']
	def __str__(self):
		return self.resume_name


class Post(models.Model):
	resume=models.ManyToManyField(Resume,help_text='投递的简历')
	company=models.ForeignKey(Company, on_delete=models.CASCADE,help_text='所属公司')
	post_name=models.CharField(max_length=255,help_text='职位名称')
	salary=models.CharField(max_length=255,help_text='薪资')
	work_place=models.CharField(max_length=255,help_text='工作地点')
	experience_require=models.CharField(max_length=255,help_text='工作经验要求')
	graduate_require=models.CharField(max_length=255,help_text='毕业院校要求')
	recruit_number=models.CharField(max_length=255,help_text='招聘人数')
	post_info=models.TextField(help_text='岗位介绍')
	update_datetime=models.DateTimeField(auto_now=True,help_text='发布时间')
	class Meta:
		db_table='post'
		ordering=['update_datetime']
	def __str__(self):
		return self.post_name

class PostTag(models.Model):
	post=models.ForeignKey(Post, on_delete=models.CASCADE,help_text='所属岗位')
	tag_name=models.CharField(max_length=255,help_text='标签名称')
	class Meta:
		db_table='post_tag'
	def __str__(self):
		return self.tag_name

class WorkExperience(models.Model):
	resume=models.ForeignKey(Resume,on_delete=models.CASCADE,help_text='所属简历')
	company_name=models.CharField(max_length=255,help_text='公司名称')
	post_name=models.CharField(max_length=255,help_text='职位名称')
	salary=models.CharField(max_length=255,help_text='薪资')
	start_date=models.CharField(max_length=255,help_text='开始时间')
	end_date=models.CharField(max_length=255,help_text='结束时间')
	work_detail=models.CharField(max_length=255,help_text='工作描述')
	class Meta:
		db_table='work_experience'
	def __str__(self):
		return self.post_name

class ProjectExperience(models.Model):
	resume=models.ForeignKey(Resume,on_delete=models.CASCADE,help_text='所属简历')
	project_name=models.CharField(max_length=255,help_text='项目名称')
	project_detail=models.CharField(max_length=255,help_text='项目描述')
	start_date=models.CharField(max_length=255,help_text='开始时间')
	end_date=models.CharField(max_length=255,help_text='结束时间')
	class Meta:
		db_table='project_experience'
	def __str__(self):
		return self.project_name

class EducateExperience(models.Model):
	resume=models.ForeignKey(Resume,on_delete=models.CASCADE,help_text='所属简历')
	school_name=models.CharField(max_length=255,help_text='学校名称')
	profession=models.CharField(max_length=255,help_text='专业')
	record=models.CharField(max_length=255,help_text='学历')
	start_date=models.CharField(max_length=255,help_text='开始时间')
	end_date=models.CharField(max_length=255,help_text='结束时间')
	class Meta:
		db_table='educate_experience'
	def __str__(self):
		return self.school_name

class Skill(models.Model):
	resume=models.ForeignKey(Resume,on_delete=models.CASCADE,help_text='所属简历')
	skill_name=models.CharField(max_length=255,help_text='技能名称')
	level=models.CharField(max_length=255,help_text='掌握程度')
	use_time=models.CharField(max_length=255,help_text='使用时长')
	class Meta:
		db_table='skill'
	def __str__(self):
		return self.skill_name