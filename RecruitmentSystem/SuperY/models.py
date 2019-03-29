from django.db import models

class Applicant(models.Model):
	phone_number=models.CharField(max_length=255,help_text='手机号码',unique=True)
	person_name=models.CharField(max_length=255,help_text='注册人姓名',default='')
	passwd=models.CharField(max_length=255,help_text='密码',default='')						#删除了头像字段，主页显示直接调用简历中的头像即可
	register_datetime=models.DateTimeField(auto_now_add=True,help_text='注册时间',null=True)
	login_random=models.CharField(max_length=255,help_text='登陆号',default='')
	class Meta:
		db_table='applicant'
		ordering=['-register_datetime']
	def __str__(self):
		return self.phone_number+'['+self.person_name+']'

class Company(models.Model):
	phone_number=models.CharField(max_length=255,help_text='手机号码',unique=True)			#手机号都设置唯一，索引查询更快
	person_name=models.CharField(max_length=255,help_text='注册人姓名',default='')
	passwd=models.CharField(max_length=255,help_text='密码',default='')
	business_licence=models.ImageField(upload_to='company',default='',help_text='营业执照')
	company_name=models.CharField(max_length=255,help_text='公司名称',default='')
	register_datetime=models.DateTimeField(auto_now_add=True,help_text='注册时间',null=True)
	is_check=models.BooleanField(default=False,help_text='是否验证')
	company_info=models.TextField(default='',help_text='公司简介')
	company_type=models.CharField(default='',max_length=255,help_text='公司类型')
	staff_number=models.CharField(default='',max_length=255,help_text='员工数')
	address=models.CharField(default='',max_length=255,help_text='公司地址')
	login_random=models.CharField(max_length=255,help_text='登陆号',default='')
	class Meta:
		db_table='company'
		ordering=['-register_datetime']
	def __str__(self):
		return self.company_name

class ApplicantSearch(models.Model):
	applicant=models.ForeignKey(Applicant,on_delete=models.CASCADE,help_text='搜索人',null=True)
	search_word=models.CharField(max_length=255,help_text='搜索关键词',default='')
	search_datetime=models.DateTimeField(auto_now_add=True,help_text='搜索时间')
	class Meta:
		db_table='applicant_search'
		ordering=['-search_datetime']
	def __str__(self):
		return self.search_word

class CompanySearch(models.Model):
	company=models.ForeignKey(Company,on_delete=models.CASCADE,help_text='搜索人',null=True)
	search_word=models.CharField(max_length=255,help_text='搜索关键词',default='')
	search_datetime=models.DateTimeField(auto_now_add=True,help_text='搜索时间')
	class Meta:
		db_table='company_search'
		ordering=['search_datetime']
	def __str__(self):
		return self.search_word

class Resume(models.Model):
	applicant=models.OneToOneField(Applicant,on_delete=models.CASCADE,help_text='所属求职者',null=True)
	head_pic=models.ImageField(upload_to='resume',null=True)
	applicant_name=models.CharField(max_length=255,help_text='求职者名称',default='')
	sex=models.CharField(max_length=255,help_text='性别',default='')
	age=models.CharField(max_length=255,help_text='年龄',default='')
	birth_place=models.CharField(max_length=255,help_text='出生地',default='')
	experience=models.CharField(max_length=255,help_text='工作经验',default='')
	phone_number=models.CharField(max_length=255,help_text='手机号',default='')
	mail=models.CharField(max_length=255,help_text='邮箱',default='')
	apply_status=models.CharField(max_length=255,help_text='求职状态',default='')
	graduate=models.CharField(max_length=255,help_text='毕业院校',default='')
	profession=models.CharField(max_length=255,help_text='期望从事行业',default='')
	work_place=models.CharField(max_length=255,help_text='期望工作地点',default='')
	post_name=models.CharField(max_length=255,help_text='期望职位',default='')
	salary=models.CharField(max_length=255,help_text='期望薪资',default='')
	work_nature=models.CharField(max_length=255,help_text='工作性质',default='')
	self_judge=models.TextField(help_text='自我评价',default='')
	update_datetime=models.DateTimeField(auto_now=True,help_text='更新时间')
	company_look=models.ManyToManyField(Company,help_text='浏览的企业')
	is_useful=models.BooleanField(default=False,help_text='是否可用')
	class Meta:
		db_table='resume'
		ordering=['-update_datetime']
	def __str__(self):
		return self.resume_name

class Tag(models.Model):
	tag_name=models.CharField(max_length=255,help_text='标签名称')
	class Meta:
		db_table='tag'
	def __str__(self):
		return self.tag_name

class Post(models.Model):
	resume=models.ManyToManyField(Resume,help_text='投递的简历')
	company=models.ForeignKey(Company, on_delete=models.CASCADE,help_text='所属公司')
	post_name=models.CharField(max_length=255,help_text='职位名称',default='')
	salary=models.CharField(max_length=255,help_text='薪资',default='')
	work_place=models.CharField(max_length=255,help_text='工作地点',default='')
	experience_require=models.CharField(max_length=255,help_text='工作经验要求',default='')
	graduate_require=models.CharField(max_length=255,help_text='毕业院校要求',default='')
	recruit_number=models.CharField(max_length=255,help_text='招聘人数',default='')
	post_info=models.TextField(help_text='岗位介绍',default='')
	update_datetime=models.DateTimeField(auto_now=True,help_text='发布时间')
	tag=models.ManyToManyField(Tag)
	class Meta:
		db_table='post'
		ordering=['update_datetime']
	def __str__(self):
		return self.post_name

class WorkExperience(models.Model):
	resume=models.ForeignKey(Resume,on_delete=models.CASCADE,help_text='所属简历')
	company_name=models.CharField(max_length=255,help_text='公司名称',default='')
	post_name=models.CharField(max_length=255,help_text='职位名称',default='')
	salary=models.CharField(max_length=255,help_text='薪资',default='')
	start_date=models.CharField(max_length=255,help_text='开始时间',default='')
	end_date=models.CharField(max_length=255,help_text='结束时间',default='')
	work_detail=models.CharField(max_length=255,help_text='工作描述',default='')
	class Meta:
		db_table='work_experience'
	def __str__(self):
		return self.post_name

class ProjectExperience(models.Model):
	resume=models.ForeignKey(Resume,on_delete=models.CASCADE,help_text='所属简历')
	project_name=models.CharField(max_length=255,help_text='项目名称',default='')
	project_detail=models.CharField(max_length=255,help_text='项目描述',default='')
	start_date=models.CharField(max_length=255,help_text='开始时间',default='')
	end_date=models.CharField(max_length=255,help_text='结束时间',default='')
	class Meta:
		db_table='project_experience'
	def __str__(self):
		return self.project_name

class EducateExperience(models.Model):
	resume=models.ForeignKey(Resume,on_delete=models.CASCADE,help_text='所属简历')
	school_name=models.CharField(max_length=255,help_text='学校名称',default='')
	profession=models.CharField(max_length=255,help_text='专业',default='')
	record=models.CharField(max_length=255,help_text='学历',default='')
	start_date=models.CharField(max_length=255,help_text='开始时间',default='')
	end_date=models.CharField(max_length=255,help_text='结束时间',default='')
	class Meta:
		db_table='educate_experience'
	def __str__(self):
		return self.school_name

class Skill(models.Model):
	resume=models.ForeignKey(Resume,on_delete=models.CASCADE,help_text='所属简历')
	skill_name=models.CharField(max_length=255,help_text='技能名称',default='')
	level=models.CharField(max_length=255,help_text='掌握程度',default='')
	use_time=models.CharField(max_length=255,help_text='使用时长',default='')
	class Meta:
		db_table='skill'
	def __str__(self):
		return self.skill_name