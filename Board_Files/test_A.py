import ujson as json


class TestAsteroid:
    def test_asteroid(self, iterations):
        n = iterations
        response = ({'header': 'test_asteroid'})
        response.update({'body': [[(i, 0), (0, abs(abs(i) - n)), (0, -(abs(abs(i) - n)))] for i in range(-n, n + 1)]})
        jsnd_response = json.dumps(response)
        return jsnd_response
