from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from django.core.urlresolvers import NoReverseMatch

from utils.messages import error_msg, success_msg

from contests.models import Contest, Round
from problems.models import Problem

# decorator which handles non-existsing contests
def get_contest(original_function):
	def new_function(request, **kwargs):
		try:
			kwargs['contest'] = Contest.objects.get(id = kwargs['contest'])
		except Contest.DoesNotExist:
			error_msg(request, "Contest with id={} does not exist.".format(kwargs['contest']))
			return redirect('contests-contests')
		return original_function(request, **kwargs)
	return new_function

# decorator which handles non-existsing rounds and which checks whether this round belongs to the contest, or not
def get_round(original_function):
	def new_function(request, **kwargs):
		try:
			kwargs['round'] = Round.objects.get(id = kwargs['round'])
		except Round.DoesNotExist:
			error_msg(request, "Round with id={} does not exist.".format(kwargs['round']))
			return redirect('contests-contest', kwargs['contest'].id)
		if kwargs['round'].contest != kwargs['contest']:
			error_msg(request, "Round with id={} does not belong to this contest.".format(kwargs['round'].id))
			return redirect('contests-contest', kwargs['contest'].id)
		return original_function(request, **kwargs)
	return new_function


from problems.views import get_problem

@login_required
@get_contest
@get_round
@get_problem
def detach_problem(request, contest, round, problem):
	round.problems.remove(problem)
	success_msg(request, "The problem was detached successfully.")

	if request.method == 'GET':
		next_page = request.GET.get('next', '')
		try:
			return redirect(next_page)
		except NoReverseMatch:
			pass

	return redirect('contests-contest', contest.id)

@login_required
@get_contest
@get_round
@get_problem
def attach_problem(request, contest, round, problem):
	round.problems.add(problem)
	success_msg(request, "The problem was attached successfully.")

	if request.method == 'GET':
		next_page = request.GET.get('next', '')
		try:
			return redirect(next_page)
		except NoReverseMatch:
			pass

	return redirect('contests-contest', contest.id)


@login_required
@get_contest
@get_round
def attach(request, contest, round):
	context = {}

	search_string = ''

	if request.method == 'GET':
		search_string = request.GET.get('search', '')
	
	context['problems'] = Problem.objects.filter(title__icontains=search_string).order_by('title').all()
	context['search_string'] = search_string

	context['contest'] = contest
	context['round'] = round
	return render(request, 'contests/contest/round/attach.html', context)


@login_required
@get_contest
@get_round
def round_edit(request, contest, round):
	context = {}

	if request.method == 'POST':
		round.name = request.POST.get('name', '')

		if request.POST.get('remove', 'no-remove') != 'no-remove':
			round.delete()
			success_msg(request, "Round was deleted successfully.")
			return redirect('contests-contest', contest.id)

		try:
			round.save()
			success_msg(request, "Round was edited successfully.")
			return redirect('contests-contest', contest.id)

		except round.Error as error:
			error_msg(request, "Could not edit the round because of some errors.")
			context['error'] = error

	context['contest'] = contest
	context['round'] = round
	return render(request, 'contests/contest/round/edit.html', context)


@login_required
@get_contest
def round_add(request, contest):
	context = {}
	round = Round()
	if request.method == 'POST':
		round.name = request.POST.get('name', '')
		round.contest = contest
		try:
			round.save()
			success_msg(request, "The round was created successfully.")
			return redirect('contests-contest', contest.id)

		except round.Error as error:
			error_msg(request, "The round couldn't be created because of some errors.")
			context['error'] = error

	context['contest'] = contest
	return render(request, 'contests/contest/round/add.html', context)


@login_required
@get_contest
def edit(request, contest):
	context = {}
	if request.method == 'POST':
		contest.name = request.POST.get('name', '')
		contest.description = request.POST.get('description', '')
		contest.begin_date = request.POST.get('begin_date', '')
		contest.end_date = request.POST.get('end_date' ,'')

		if request.POST.get('remove', 'no-remove') != 'no-remove':
			contest.delete()
			error_msg(request, "Contest was deleted successfully.")
			return redirect('contests-contests')

		try:
			contest.save()
			success_msg(request, "Contest was edited successfully.")
			return redirect('contests-contest', contest.id)
		
		except contest.Error as error:
			error_msg(request, "Could not create the contest because of some errors.")
			context['error'] = error

	context['contest'] = contest
	return render(request, "contests/contest/edit.html", context)


@login_required
def add(request):
	contest = Contest()
	context = {}

	if request.method == 'POST':
		contest.name = request.POST.get('name', '')
		contest.description = request.POST.get('description', '')
		contest.begin_date = request.POST.get('begin_date', '')
		contest.end_date = request.POST.get('end_date', '')

		try:
			contest.save()
			success_msg(request, "Contest was created successfully.")
			return redirect('contests-contest', contest.id)

		except contest.Error as error:
			error_msg(request, "Could not create the contest because of some errors.")
			context['error'] = error

	context['contest'] = contest
	return render(request, 'contests/contest/add.html', context)


@login_required
@get_contest
def contest(request, contest):
	context = {}
	context['contest'] = contest
	context['active_round'] = request.session.get('active_round', -1)
	return render(request, 'contests/contest/contest.html', context)


@login_required
def contests(request):
	contests = Contest.objects.order_by('-begin_date', '-end_date').all()
	context = {}
	context['contests'] = contests
	return render(request, 'contests/contests.html', context)
