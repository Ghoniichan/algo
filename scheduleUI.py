import tkinter as tk
from tkinter import ttk
import scheduler

class ScrollableFrame(ttk.Frame):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        canvas = tk.Canvas(self, height=600)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

class PreferencesGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Customize Your Preferences")
        self.geometry("620x700")
        self.courses = []
        scrollable = ScrollableFrame(self)
        scrollable.pack(fill=tk.BOTH, expand=True)
        self.main_frame = scrollable.scrollable_frame

        ttk.Label(self.main_frame, text="Customize Your Preferences", font=("Arial", 14, "bold")).pack(pady=10)

        self.init_course_section_inputs()
        ttk.Separator(self.main_frame, orient="horizontal").pack(fill=tk.X, pady=10)
        self.init_preferences_section()
        ttk.Button(self.main_frame, text="Get Schedule", command=self.save_preferences).pack(pady=20)

    def init_preferences_section(self):
        frame = ttk.Frame(self.main_frame)
        frame.pack(fill=tk.BOTH, expand=True)

        # Preferred Start/End Time
        ttk.Label(frame, text="Preferred Start Time:").grid(row=0, column=0, sticky="w")
        self.start_time = tk.StringVar(value="10:00 AM")
        start_times = [f"{h}:00 {'AM' if h < 12 else 'PM'}" for h in list(range(7, 12)) + list(range(12, 18))]
        ttk.Combobox(frame, values=start_times, textvariable=self.start_time, state="readonly").grid(row=0, column=1, padx=5, pady=2)

        ttk.Label(frame, text="Preferred End Time:").grid(row=1, column=0, sticky="w")
        self.end_time = tk.StringVar(value="5:00 PM")
        end_times = [f"{h}:00 {'AM' if h < 12 else 'PM'}" for h in list(range(7, 12)) + list(range(12, 22))]
        ttk.Combobox(frame, values=end_times, textvariable=self.end_time, state="readonly").grid(row=1, column=1, padx=5, pady=2)

        ttk.Label(frame, text="Preference Importance (1 - Not Important, 10 - Very)", font=("Arial", 10, "italic")).grid(row=3, column=0, columnspan=2, pady=15)

        def add_pref_row(row, text, default_val):
            var = tk.IntVar(value=1)
            cb = ttk.Checkbutton(frame, text=text, variable=var)
            cb.grid(row=row, column=0, sticky="w", pady=5)

            slider_val = tk.IntVar(value=default_val)
            slider = ttk.Scale(frame, from_=1, to=10, orient="horizontal", variable=slider_val)
            slider.grid(row=row, column=1, padx=5, sticky="ew", pady=5)

            val_label = ttk.Label(frame, textvariable=slider_val, width=3)
            val_label.grid(row=row, column=2, sticky="w")

            def toggle_slider():
                state = "normal" if var.get() else "disabled"
                slider.config(state=state)

            var.trace_add("write", lambda *args: toggle_slider())
            toggle_slider()

            return var, slider_val

        self.prefs = {}
        self.prefs['prefer_free_days'] = add_pref_row(4, "Prefer Free Days:", 8)
        self.prefs['avoid_morning_classes'] = add_pref_row(5, "Avoid Morning Classes:", 10)
        self.prefs['prefer_early_dismissal'] = add_pref_row(6, "Prefer Early Dismissal:", 6)
        self.prefs['prefer_consecutive_classes'] = add_pref_row(7, "Prefer Consecutive Classes:", 3)
        self.prefs['prefer_long_breaks'] = add_pref_row(8, "Prefer Long Breaks:", 7)

        # Breaks and Algorithm
        ttk.Label(frame, text="Preferred Break Time (minutes):").grid(row=9, column=0, sticky="w", pady=10)
        self.pref_break_time = tk.IntVar(value=60)
        ttk.Combobox(frame, values=[15, 30, 45, 60, 75, 90], textvariable=self.pref_break_time, state="readonly").grid(row=9, column=1, padx=5)

        ttk.Label(frame, text="Scheduling Algorithm:").grid(row=11, column=0, sticky="w", pady=10)
        self.scheduling_algo = tk.StringVar(value="Choose Algorithm")
        ttk.Combobox(frame, values=["Greedy Algorithm", "Dynamic Algorithm", "Backtracking Algorithm"],
                     textvariable=self.scheduling_algo, state="readonly").grid(row=11, column=1, padx=5)

    def init_course_section_inputs(self):
        section_frame = ttk.LabelFrame(self.main_frame, text="Courses & Sections")
        section_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        ttk.Label(section_frame, text="Course Code:").grid(row=0, column=0, sticky="w")
        self.course_code = tk.StringVar()
        ttk.Entry(section_frame, textvariable=self.course_code).grid(row=0, column=1)

        ttk.Label(section_frame, text="Course Name:").grid(row=1, column=0, sticky="w")
        self.course_name = tk.StringVar()
        ttk.Entry(section_frame, textvariable=self.course_name).grid(row=1, column=1)

        ttk.Button(section_frame, text="Add Course", command=self.add_course).grid(row=3, column=0, columnspan=2, pady=10)

        ttk.Label(section_frame, text="Section ID:").grid(row=4, column=0, sticky="w")
        self.section_id = tk.StringVar()
        ttk.Entry(section_frame, textvariable=self.section_id).grid(row=4, column=1)

        ttk.Label(section_frame, text="Course ID:").grid(row=5, column=0, sticky="w")
        self.section_course_id = tk.StringVar()
        ttk.Entry(section_frame, textvariable=self.section_course_id).grid(row=5, column=1)

        ttk.Label(section_frame, text="Professor:").grid(row=6, column=0, sticky="w")
        self.professor = tk.StringVar()
        ttk.Entry(section_frame, textvariable=self.professor).grid(row=6, column=1)

        ttk.Label(section_frame, text="Start Time:").grid(row=7, column=0, sticky="w")
        self.section_start = tk.StringVar()
        ttk.Entry(section_frame, textvariable=self.section_start).grid(row=7, column=1)

        ttk.Label(section_frame, text="End Time:").grid(row=8, column=0, sticky="w")
        self.section_end = tk.StringVar()
        ttk.Entry(section_frame, textvariable=self.section_end).grid(row=8, column=1)

        # Days
        ttk.Label(section_frame, text="Days:").grid(row=9, column=0, sticky="nw")
        self.days_vars = {}
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
        days_frame = ttk.Frame(section_frame)
        days_frame.grid(row=9, column=1, sticky="w")
        for i, day in enumerate(days):
            var = tk.BooleanVar()
            chk = ttk.Checkbutton(days_frame, text=day, variable=var)
            chk.grid(row=i // 2, column=i % 2, sticky="w")
            self.days_vars[day] = var

        ttk.Button(section_frame, text="Add Section", command=self.add_section).grid(row=10, column=0, columnspan=2, pady=10)

    def add_course(self):
        course_code = self.course_code.get()
        course_name = self.course_name.get()
        if not course_code or not course_name:
            print("Please fill in all fields.")
            return
        course = scheduler.Course(course_code, course_name)

        #check if course already exists
        for c in self.courses:
            if c.course_id == course_code:
                print("Course already exists.")
                return
        self.courses.append(course)

        #print courses
        print("Courses:")
        for c in self.courses:
            print(f"Course ID: {c.course_id}, Course Name: {c.course_name}")

    def add_section(self):
        section_id = self.section_id.get()
        section_course_id = self.section_course_id.get()

        #get days and encode them: Monday = 0, Tuesday = 1, Wednesday = 2, Thursday = 3, Friday = 4, Saturday = 5
        d = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
        days = [day for day, var in self.days_vars.items() if var.get()]
        days = [d.index(day) for day in days]
        
        start_time = self.section_start.get()
        start_hour = int(start_time.split(':')[0])
        start_minute = int(start_time.split(':')[1])
        end_time = self.section_end.get()
        end_hour = int(end_time.split(':')[0])
        end_minute = int(end_time.split(':')[1])
        professor = self.professor.get()

        if not section_id or not section_course_id or not professor or not start_time or not end_time or not days:
            print("Please fill in all fields.")
            return
        
        # Check if course exists
        course = next((c for c in self.courses if c.course_id == section_course_id), None)
        if not course:
            print("Course does not exist.")
            return
        # Check if section already exists
        for c in self.courses:
            if c.course_id == section_course_id:
                for s in c.sections:
                    if s.section_id == section_id:
                        print("Section already exists.")
                        return
        # Create section
        #phys101.add_section(Section("3", "PHYS101", [2, 4], 13*60, 14*60+30, "Jackson"))
        section = scheduler.Section(section_id, section_course_id, days, start_hour*60+start_minute, end_hour*60+end_minute, professor)
        course.add_section(section)
        print(f"Added section {section_id} to course {section_course_id}")
        # Print sections
        print("Sections:")
        for c in self.courses:
            print(f"Course ID: {c.course_id}, Course Name: {c.course_name}")
            for s in c.sections:
                print(type(s))
        
    def save_preferences(self):

        start_hour = int(self.start_time.get().split(':')[0])
        end_hour = int(self.end_time.get().split(':')[0])

        p = {k: slider.get() for k, (var, slider) in self.prefs.items()}
        preferences = scheduler.StudentPreferences()
        preferences.no_morning_weight = p.get('avoid_morning_classes')      # Strong preference for no morning classes
        preferences.free_days_weight = p.get('prefer_free_days')         # Strong preference for free days
        preferences.early_dismissal_weight = p.get('prefer_early_dismissal')   # Moderate preference for early dismissal
        preferences.consecutive_classes_weight = p.get('prefer_consecutive_classes')  # Low preference for consecutive classes
        preferences.long_breaks_weight = p.get('prefer_long_breaks')       # High preference for long breaks
        
        preferences.preferred_earliest_time = start_hour * 60  # No classes before 10 AM
        preferences.preferred_latest_time = end_hour * 60    # No classes after 5 PM
        preferences.preferred_break_time = int(self.pref_break_time.get())

        algo = self.scheduling_algo.get()

        if algo == "Greedy Algorithm":
            sched = scheduler.greedy_schedule_optimizer(self.courses, preferences)
        elif algo == "Dynamic Algorithm":
            sched = scheduler.dynamic_programming_scheduler(self.courses, preferences)
        elif algo == "Backtracking Algorithm":
            sched = scheduler.backtracking_scheduler(self.courses, preferences)
        else:
            print("Please select a scheduling algorithm.")
            return
        
        sched.print_schedule()

if __name__ == "__main__":
    app = PreferencesGUI()
    app.mainloop()
