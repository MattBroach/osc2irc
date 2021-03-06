from .responses import ActionResponse


class InvalidActionError(Exception):
    """
    Raised if the action type passed to a Command is not in `allowed_acctions`
    """
    pass


class Command:
    """
    Handles the current value and processing of an IRC command, which is expected to be of the form of:

        !NAME ACTION <VALUE>

    where NAME is the name of the command, ACTION is the action to perform, and VALUE is an optional
    third argument for actions that must set a particular value.

    running an action should return a CommandResponse object, which will contain a VALUE
    """
    def __init__(
        self,
        name=None,
        min=0.0,
        max=1.0,
        delta=0.05,
        initial=0.0,
        current=None,
        outputs={},
        echo='',
        allowed_actions=[],
    ):
        if name is None:
            raise ValueError(
                'name is a required keyword argument for a Command object'
            )

        self.name = name
        self.outputs = outputs
        self.min = min
        self.max = max
        self.delta = delta
        self.initial = initial,
        self.current = current if current is not None else initial
        self.echo = echo
        self.allowed_actions = allowed_actions

    def __str__(self):
        return self.name

    def run_action(self, action=None, value=None):
        """
        Checks action validity and the passes the action to the proper function
        """
        if action is None:
            return ActionResponse(self.echo)

        action = action.lower()

        if action not in self.allowed_actions:
            raise InvalidActionError(
                '"{}" is not a valid action for command "{}"'.format(action, self.name.upper())
            )

        action_func = getattr(
            self, 'run_{}'.format(action), lambda *args, **kwargs: None
        )

        return action_func(value=value)

    def run_increment(self, **kwargs):
        """
        Increase the current value by `self.delta_val`, restricting self.max

        return a valid ActionResponse object
        """
        if self.current == self.max:
            return ActionResponse(self.max_msg)

        self.current += self.delta

        if self.current > self.max:
            self.current = self.max

        return ActionResponse(
            self.max_msg,
            self.current,
            self.outputs,
        )

    def run_decrement(self, **kwargs):
        """
        Increase the current value by `self.delta_val`, restricting self.max

        return a valid CommandResponse object
        """
        if self.current == self.min:
            return ActionResponse(self.min_msg)

        self.current -= self.delta

        if self.current < self.min:
            self.current = self.min

        return ActionResponse(
            self.min_msg,
            self.current,
            self.outputs,
        )

    def run_set(self, value, **kwargs):
        """
        Set the current value to the passed value, restricting to the the self.min and self.max
        """
        try:
            value = float(value)
        except (ValueError, TypeError) as e:
            return ActionResponse(self.invalid_value_msg)

        if value > self.max or value < self.min:
            return ActionResponse(self.get_out_of_bounds_msg(value))

        prev_value = self.current
        self.current = value
        response_msg = self.min_msg if prev_value > self.current else self.max_msg

        return ActionResponse(
            response_msg,
            self.current,
            self.outputs,
        )

    def run_get(self, **kwargs):
        """
        Returns the current value
        """
        return ActionResponse(
            self.range_msg,
            self.current,
            self.outputs,
        )

    @property
    def min_msg(self):
        """
        Generates message with current value and minimum values for use in ActionResponse objects
        """
        return "{} is at {} (Min {})".format(self.name.upper(), round(self.current, 3), self.min)

    @property
    def max_msg(self):
        """
        Generates message with current value and maximum values for use in ActionResponse objects
        """
        return "{} is at {} (Max {})".format(self.name.upper(), round(self.current, 3), self.max)

    @property
    def range_msg(self):
        """
        Generates message with the current value and the min/max values for us in ActionResponse objects
        """
        return "{} is at {} (Min {}, Max {})".format(
            self.name.upper(), round(self.current, 3), self.max, self.min
        )

    @property
    def invalid_value_msg(self):
        """
        Generates message stating value passed is not a valid value (usually because a float
        was expected but not received)
        """
        return '"{} set" requires a number value between {} and {}'.format(
            self.name.upper(), self.min, self.max
        )

    def get_out_of_bounds_msg(self, value):
        """
        Generates message stating value passed is out of bounds, and requesting a proper value
        """
        return "{} is out of bounds for {} (Min {}, Max {})".format(
           value, self.name.upper(), self.min, self.max
        )
