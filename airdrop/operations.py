"""Operations, otherwise known as steps that the airdrop program has to take to complete it's task."""
"""Author: spunk-developer <xspunk.developer@gmail.com>"""

def validate_supply_balance(input) -> float:
	"""Validates any arbitrary `input` value to see if it is a number that is greater than 0.

	Args:
		input (Any): Arbitrary

	Raises:
		RuntimeError: _description_

	Returns:
		float: _description_
	"""

	# We parse the actual input into a float or an int. If this fails, the error is raised to the caller.
	try:
		if type(input) is not (float | int):
			input = float(input)
	except:
		raise

	# XRP minimum and maximum number enforcement.
	if input <= 0:
		raise RuntimeError(f'Input "{ input }" is equal to or smaller than 0')
	elif input > 100000000000000000:
		raise RuntimeError(f'Input "{ input }" is larger than maximum allowed integer 100000000000000000')

	return input
