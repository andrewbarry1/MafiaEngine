# basic holding class for data about visits
# has some comparison function overrides for night action priority
class Visit:
    def __init__(self, visitor, visited, callback, priority):
        self.visitor = visitor
        self.visited = visited
        self.callback = callback
        self.priority = priority

    def __lt__(self, other):
        return (self.priority.value < other.priority.value)
    def __gt__(self, other):
        return (self.priority.value > other.priority.value)
    def __eq__(self, other):
        return (self.priority.value == other.priority.value)
    def __ne__(self, other):
        return not(self.priority.value == other.priority.value)
