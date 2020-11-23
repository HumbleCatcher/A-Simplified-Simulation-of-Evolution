import helper_functions
from models.simulation import Simulation
from structs import point

thread_pool = helper_functions.ThreadPoolExecutorStackTraced(max_workers=1)


class SimulationController(object):
    PAUSE = 0
    PLAY = 1
    RUNNING = 2

    def __init__(self, canvas, canvas_width, canvas_height, speed_var, seed_var, start_population_var, food_count_var):
        self.canvas = canvas
        self.canvas_width = canvas_width
        self.canvas_height = canvas_height
        self.state = SimulationController.PAUSE
        self.speed_var = speed_var
        self.seed_var = seed_var
        self.start_population_var = start_population_var
        self.food_count_var = food_count_var
        self.reset()

    def update_canvas(self):
        all_canvas_ids = list(self.canvas.find_all())
        for drawable in self.simulation.all_drawables:
            if drawable.canvas_id is None:
                drawable.canvas_id = self.canvas.create_circle(drawable.position.x, drawable.position.y,
                                                               drawable.radius,
                                                               fill=drawable.color.to_hex())
            else:
                dx = drawable.position.x - drawable.last_drawn_position.x
                dy = drawable.position.y - drawable.last_drawn_position.y
                self.canvas.move(drawable.canvas_id, dx, dy)
                drawable.last_drawn_position = point.Point(drawable.position.x, drawable.position.y)
                all_canvas_ids.remove(drawable.canvas_id)
        for unused in all_canvas_ids:
            self.canvas.delete(unused)
        self.canvas.update()

    def play(self):
        if self.state != SimulationController.RUNNING:
            self.state = SimulationController.RUNNING

            def callback(this_future):
                try:
                    result = this_future.result()
                except Exception:
                    raise
                if result == Simulation.FINISHED:
                    self.pause()
                    self.show_message('The simulation has finished')
                else:
                    self.update_canvas()
                    if self.state != SimulationController.PAUSE:
                        self.state = SimulationController.PLAY
                        self.play()

            future = thread_pool.submit(self.simulation.step, self.speed_var.get())
            future.add_done_callback(callback)

    def pause(self):
        self.state = SimulationController.PAUSE

    def reset(self):
        self.canvas.delete('all')
        if self.state != SimulationController.PAUSE:
            self.pause()
        self.simulation = Simulation(self.canvas_width, self.canvas_height, self.seed_var.get(), self.start_population_var.get(), self.food_count_var.get())
        self.update_canvas()

    def save(self):
        self.simulation.save()

    def show_message(self, msg):
        self.canvas.delete('all')
        self.canvas.create_text(self.canvas_width / 2, self.canvas_height / 2, fill='white', text=msg)
