from __future__ import division
import ast
import operator
import math

PLUGIN_METADATA = {
	'id': 'simple_calculator',
	'version': '1.0.0',
	'name': 'Simple in-game calculator',
	'author': 'Fallen_Breath',
	'link': 'https://github.com/TISUnion/Calculator'
}

MAX_RESULT_LEN = 1000  # maximum result string length
MAX_POWER_LEN = 10000  # simpleeval.MAX_POWER override
ENABLE_SIMPLEEVAL = True  # if enable simpleeval for better calculator if it's doable


if ENABLE_SIMPLEEVAL:
	try:
		import simpleeval
	except ImportError:
		simpleeval = None
else:
	simpleeval = None


def eval_or_error(func, arg):
	try:
		return func(arg)
	except Exception as e:
		return '{}: {}'.format(type(e).__name__, e)


def naive_eval(text):
	whitelist = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', ' ', '.', '+', '-', '*', '/', '(', ')', '<', '>', '=']
	text = text.replace('**', '')  # to avoid eeasee
	text_clean = ''
	for c in text:
		if c in whitelist:
			text_clean += c

	if len(text_clean) == 0:
		return None
	return eval_or_error(eval, text_clean)


def simple_eval(text):
	def merge(a, b):
		ret = a.copy()
		ret.update(b)
		return ret

	simpleeval.MAX_POWER = MAX_POWER_LEN
	s = simpleeval.SimpleEval(
		operators=merge(simpleeval.DEFAULT_OPERATORS, {
			ast.BitXor: operator.xor,
			ast.BitAnd: operator.and_,
			ast.BitOr: operator.or_,
			ast.RShift: operator.rshift,
			ast.LShift: operator.lshift,
		})
	)
	for k, v in math.__dict__.items():
		if not k.startswith('_'):
			if type(v) in [int, float]:
				s.names[k] = v
			elif callable(v) and k not in ['exp', 'expm1', 'ldexp', 'pow', 'factorial']:
				s.functions[k] = v
	s.functions.update({
		'hex': lambda x: hex(x).replace('0x', '', 1).rstrip('L').upper(),
		'bin': lambda x: bin(x).replace('0b', '', 1).rstrip('L'),
		'oct': lambda x: oct(x).replace('0o', '', 1).rstrip('L'),
		'bool': bool
	})
	return eval_or_error(s.eval, text)


def calc(text):
	if not text:
		return None
	result = simple_eval(text) if simpleeval else naive_eval(text)
	if result is None:
		return None
	elif type(result) is float:
		result = round(result, 12)  # makes sin(pi) look nicer
	result = str(result)
	if len(result) > MAX_RESULT_LEN:
		result = result[:max(MAX_RESULT_LEN - 3, 0)] + '...'
	return result


def work(server, info):
	if info.content.startswith('=='):
		result = calc(info.content[2:])
		if result:
			info.cancel_send_to_server()
			server.say(result)


# MCDReforged
def on_user_info(server, info):
	if info.is_player:
		work(server, info)


def on_load(server, old):
	if simpleeval:
		server.logger.info('The simpleeval module is detected and advanced calculation mode is enabled')
	else:
		server.logger.info('simpleeval module not detected, use simple mode')
	server.register_help_message('==<exp>', 'Calculate expression§7<exp>§r')


if __name__ == '__main__':
	while True:
		print(calc(input()))
