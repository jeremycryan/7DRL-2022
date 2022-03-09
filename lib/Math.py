def lerp(start, end, through, curve=None):
    """
    Interpolates between two values.
    :param start: The starting value
    :param end: The ending value
    :param through: The proportion of
    :param curve:
    :return:
    """
    if through < 0:
        return start
    if through > 1:
        return end
    if not curve:
        return (end - start) * through + start
    else:
        return (end - start) * curve.out(through) + start


class Curve:
    def __init__(self):
        pass

    def _out(self, x):
        """
        Returns the y coordinate of the curve given an X. Does not validate input.
        :param x: The x coordinate
        :return: The y coordinate
        """

    def out(self, x):
        """
        Returns the y coordinate of the curve given an X.
        :param x: The amount through the curve, from 0 to 1.
        :return: The curve output. At x=0, it should equal 0, and at x=1, it should
            equal 1.
        """
        if not (0 <= x <= 1):
            raise ValueError("Input must be between 0 and 1")
        return self._out(x)


class PowerCurve(Curve):
    def __init__(self, acceleration_time=0.5, deceleration_time=0.5, power=2):
        """
        Generates the curve based on an acceleration time and deceleration time. Times
        should sum to no more than one second. Any excess time will just be sustained
        at the maximum speed. Power describes the exponent used during acceleration and
        deceleration, generalized from the power of two used in normal Trapezoidal
        motion profile.

        :param acceleration_time: Time to reach max speed, in seconds.
        :param deceleration_time: Time to slow down to stopped, in seconds.
        """
        super().__init__()
        if not acceleration_time + deceleration_time <= 1.0:
            raise ValueError("Acceleration time and deceleration time cannot sum to more than 1.")
        self._power = power
        self._accel_time = acceleration_time
        self._decel_time = deceleration_time
        self._max_speed = self._calculate_max_speed()

    def _calculate_max_speed(self):
        """
        Returns the maximum speed of the constant derivative part of the curve.
        :return: The maximum speed
        """
        # Assume some starting max speed
        max_speed = 1
        # This calculation works, assuming a first derivative of max_speed after acceleration
        accel_distance = max_speed * self._accel_time / self._power
        decel_distance = max_speed * self._decel_time / self._power
        coast_distance = (1 - self._accel_time - self._decel_time) * max_speed
        total_distance = accel_distance + decel_distance + coast_distance
        # Calculate how off we were, knowing we should travel exactly 1 distance
        factor = 1 / total_distance
        return factor * max_speed

    def _out(self, x):
        i_factor = 1/self._power
        if x < self._accel_time:
            return i_factor * (x/self._accel_time)**self._power * self._max_speed * self._accel_time
        elif x < 1 - self._decel_time:
            return self._max_speed * i_factor * self._accel_time + (x - self._accel_time) * self._max_speed
        else:
            return 1 - (i_factor * ((1 - x)/self._decel_time)**self._power * self._max_speed * self._decel_time)


def get_line(start, end):
    squares = [start]
    diff = end - start
    if abs(diff.y) > abs(diff.x):
        for dy in range(1, abs(diff.y) + 1):
            scale = abs(dy / diff.y)
            p = start + diff * scale
            p.x = round(p.x)
            p.y = round(p.y)
            squares.append(p)
    else:
        for dx in range(1, abs(diff.x) + 1):
            scale = abs(dx / diff.x)
            p = start + diff * scale
            p.x = round(p.x)
            p.y = round(p.y)
            squares.append(p)
    return squares
