


def hello_filter(name):
    return f'Hello {name}!'


class FilterModule(object):

  def filters(self):
    return {
      'hello': hello_filter
    }
  