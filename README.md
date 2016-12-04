# py-actor  
WARNING: IT JUST FINISHED THE BASIC REQUIREMENT  

Actor Model implemented in Python


	import pyactor


	class DemoActor(pyactor.MultiprocessingActor):

	    def __init__(self):
	        super(DemoActor, self).__init__()

	    def add(self, x, y):
	        return x + y

	    def on_receive(self, message):
	        if message.get('command') == 'add':
	            return self.add(*message.get('args'))



	actor = DemoActor.start()
	future = actor.ask({'command': 'add', 'args': [3, 4]})
	print('future result is :')
	print(future.get())
	actor.stop()
