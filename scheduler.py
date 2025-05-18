class Course:
    def __init__(self, course_id, course_name):
        self.course_id = course_id
        self.course_name = course_name
        self.sections = []
    
    def add_section(self, section):
        self.sections.append(section)
    
    def __str__(self):
        return f"{self.course_id} - {self.course_name}"


class Section:
    def __init__(self, section_id, course_id, days, start_time, end_time, professor):
        self.section_id = section_id
        self.course_id = course_id
        self.days = days  # List of days: 0=Monday, 1=Tuesday, etc.
        self.start_time = start_time  # In minutes from midnight (e.g., 9:00 AM = 540)
        self.end_time = end_time      # In minutes from midnight
        self.professor = professor
    
    def __str__(self):
        days_str = ''.join(['M' if 0 in self.days else '', 
                          'T' if 1 in self.days else '',
                          'W' if 2 in self.days else '',
                          'Th' if 3 in self.days else '',
                          'F' if 4 in self.days else ''])
        start_hour, start_min = divmod(self.start_time, 60)
        end_hour, end_min = divmod(self.end_time, 60)
        start_time_str = f"{start_hour}:{start_min:02d}"
        end_time_str = f"{end_hour}:{end_min:02d}"
        
        return f"Section {self.section_id} ({days_str} {start_time_str}-{end_time_str}, Prof. {self.professor})"


class StudentPreferences:
    def __init__(self):
        # Preference weights (1-10, 10 is highest priority)
        self.early_dismissal_weight = 5  # Prefer schedules that end early
        self.no_morning_weight = 8      # Avoid morning classes
        self.long_breaks_weight = 3     # Prefer longer breaks between classes
        self.consecutive_classes_weight = 7  # Prefer classes back-to-back
        self.free_days_weight = 10      # Prefer having full days off
        
        # Specific preferences
        self.preferred_earliest_time = 10 * 60  # 10:00 AM in minutes
        self.preferred_latest_time = 16 * 60    # 4:00 PM in minutes
        self.minimum_break_time = 30            # 30 minutes
        self.preferred_break_time = 60          # 1 hour
        self.max_classes_per_day = 3


class Schedule:
    def __init__(self):
        self.assigned_sections = []  # List of selected sections
        self.score = 0
    
    def add_section(self, section):
        self.assigned_sections.append(section)
    
    def has_conflicts(self):
        """Check if there are any time conflicts in the schedule"""
        for i, sec1 in enumerate(self.assigned_sections):
            for j, sec2 in enumerate(self.assigned_sections):
                if i != j:
                    # Check if sections are on the same day
                    common_days = set(sec1.days).intersection(set(sec2.days))
                    if common_days:
                        # Check for time overlap
                        if not (sec1.end_time <= sec2.start_time or sec1.start_time >= sec2.end_time):
                            return True
        return False
    
    def calculate_score(self, preferences):
        """Calculate schedule score based on student preferences"""
        if self.has_conflicts():
            return -1000  # Heavy penalty for conflicts
        
        score = 0
        day_schedules = {day: [] for day in range(5)}  # 0=Monday to 4=Friday
        
        # Group sections by day
        for section in self.assigned_sections:
            for day in section.days:
                day_schedules[day].append(section)
        
        # Sort each day's sections by start time
        for day in day_schedules:
            day_schedules[day].sort(key=lambda x: x.start_time)
        
        # Count free days (days with no classes)
        free_days = sum(1 for day in day_schedules.values() if not day)
        score += free_days * preferences.free_days_weight
        
        # Evaluate each day with classes
        for day, sections in day_schedules.items():
            if not sections:
                continue
            
            # Early dismissal preference
            last_class_end = max(section.end_time for section in sections)
            if last_class_end <= preferences.preferred_latest_time:
                score += preferences.early_dismissal_weight
            
            # No morning classes preference
            first_class_start = min(section.start_time for section in sections)
            if first_class_start >= preferences.preferred_earliest_time:
                score += preferences.no_morning_weight
            
            # Check breaks between classes
            if len(sections) > 1:
                total_break_time = 0
                good_breaks = 0
                total_gaps = 0
                
                for i in range(len(sections) - 1):
                    break_time = sections[i+1].start_time - sections[i].end_time
                    total_break_time += break_time
                    total_gaps += 1
                    
                    if break_time >= preferences.minimum_break_time:
                        good_breaks += 1
                        
                        # Reward for breaks close to preferred length
                        if abs(break_time - preferences.preferred_break_time) <= 15:  # Within 15 minutes
                            score += preferences.long_breaks_weight
                
                # All breaks are good breaks
                if good_breaks == total_gaps:
                    score += 5
                
                # Back-to-back classes preference (small breaks)
                consecutive_classes = sum(1 for i in range(len(sections) - 1) 
                                    if sections[i+1].start_time - sections[i].end_time <= 15)
                score += consecutive_classes * preferences.consecutive_classes_weight
            
            # Max classes per day preference
            if len(sections) <= preferences.max_classes_per_day:
                score += 3
        
        return score
    
    def get_sched(self):
        """Return the schedule as a formatted string"""
        # Group sections by day
        day_schedules = {day: [] for day in range(5)}  # 0=Monday to 4=Friday
        day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        
        for section in self.assigned_sections:
            for day in section.days:
                day_schedules[day].append(section)
        
        result = "\n===== YOUR OPTIMIZED SCHEDULE =====\n"
        
        for day_num, sections in day_schedules.items():
            result += f"\n{day_names[day_num]}:\n"
            if not sections:
                result += "  No classes\n"
                continue
            
            # Sort sections by start time
            sections.sort(key=lambda x: x.start_time)
            
            for section in sections:
                start_hour, start_min = divmod(section.start_time, 60)
                end_hour, end_min = divmod(section.end_time, 60)
                start_am_pm = "AM" if start_hour < 12 else "PM"
                end_am_pm = "AM" if end_hour < 12 else "PM"
                start_hour = start_hour if start_hour <= 12 else start_hour - 12
                end_hour = end_hour if end_hour <= 12 else end_hour - 12
                if start_hour == 0: start_hour = 12
                if end_hour == 0: end_hour = 12
                
                result += f"  {start_hour}:{start_min:02d} {start_am_pm} - {end_hour}:{end_min:02d} {end_am_pm}: {section.course_id} (Section {section.section_id})\n"
                
                # Show break time to next class if applicable
                if sections.index(section) < len(sections) - 1:
                    next_section = sections[sections.index(section) + 1]
                    break_time = next_section.start_time - section.end_time
                    break_hours, break_mins = divmod(break_time, 60)
                    if break_time > 0:
                        result += f"  ↓ {break_hours}h {break_mins}m break ↓\n"
        
        result += f"\nTotal Score: {self.score}\n"
        
        return result
    
    def print_schedule(self):
        """Print the schedule in a readable format"""
        # Group sections by day
        day_schedules = {day: [] for day in range(5)}  # 0=Monday to 4=Friday
        day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        
        for section in self.assigned_sections:
            for day in section.days:
                day_schedules[day].append(section)
        
        print("\n===== YOUR OPTIMIZED SCHEDULE =====")
        
        for day_num, sections in day_schedules.items():
            print(f"\n{day_names[day_num]}:")
            if not sections:
                print("  No classes")
                continue
            
            # Sort sections by start time
            sections.sort(key=lambda x: x.start_time)
            
            for section in sections:
                start_hour, start_min = divmod(section.start_time, 60)
                end_hour, end_min = divmod(section.end_time, 60)
                start_am_pm = "AM" if start_hour < 12 else "PM"
                end_am_pm = "AM" if end_hour < 12 else "PM"
                start_hour = start_hour if start_hour <= 12 else start_hour - 12
                end_hour = end_hour if end_hour <= 12 else end_hour - 12
                if start_hour == 0: start_hour = 12
                if end_hour == 0: end_hour = 12
                
                print(f"  {start_hour}:{start_min:02d} {start_am_pm} - {end_hour}:{end_min:02d} {end_am_pm}: {section.course_id} (Section {section.section_id})")
                
                # Show break time to next class if applicable
                if sections.index(section) < len(sections) - 1:
                    next_section = sections[sections.index(section) + 1]
                    break_time = next_section.start_time - section.end_time
                    break_hours, break_mins = divmod(break_time, 60)
                    if break_time > 0:
                        print(f"  ↓ {break_hours}h {break_mins}m break ↓")
        
        print("\nTotal Score:", self.score)


def greedy_schedule_optimizer(courses, preferences):
    """
    Greedy algorithm to find the best schedule based on student preferences
    """
    # Start with an empty schedule
    schedule = Schedule()
    
    # Sort courses by number of available sections (fewer options first)
    sorted_courses = sorted(courses, key=lambda c: len(c.sections))
    
    # Greedily select the best section for each course
    for course in sorted_courses:
        best_section = None
        best_score = float('-inf')
        
        # Try each section of this course
        for section in course.sections:
            # Create a temporary schedule with this section
            temp_schedule = Schedule()
            for assigned_section in schedule.assigned_sections:
                temp_schedule.add_section(assigned_section)
            temp_schedule.add_section(section)
            
            # Calculate the score
            temp_score = temp_schedule.calculate_score(preferences)
            
            # Update best section if this one is better
            if temp_score > best_score:
                best_score = temp_score
                best_section = section
        
        # Add the best section to our schedule
        if best_section:
            schedule.add_section(best_section)
    
    # Calculate final score
    schedule.score = schedule.calculate_score(preferences)
    return schedule

def dynamic_programming_scheduler(courses, preferences):
    """Find optimal schedule using dynamic programming"""
    n = len(courses)
    # dp[i][mask] represents best score for first i courses and selected sections represented by mask
    dp = {}
    selections = {}
    
    def solve(course_idx, selected_sections_mask):
        # Base case: all courses processed
        if course_idx == n:
            temp_schedule = Schedule()
            # Convert mask to actual sections
            for i, course in enumerate(courses):
                section_idx = (selected_sections_mask >> (i * 4)) & 0xF
                if section_idx < len(course.sections):
                    temp_schedule.add_section(course.sections[section_idx])
            return temp_schedule.calculate_score(preferences), {}
        
        # Return if already computed
        if (course_idx, selected_sections_mask) in dp:
            return dp[(course_idx, selected_sections_mask)], selections[(course_idx, selected_sections_mask)]
        
        best_score = float('-inf')
        best_selection = {}
        
        # Try each section of current course
        for section_idx, section in enumerate(courses[course_idx].sections):
            # Update mask with this section
            new_mask = selected_sections_mask | (section_idx << (course_idx * 4))
            
            # Create temporary schedule to check conflicts
            temp_schedule = Schedule()
            for i in range(course_idx):
                sec_idx = (selected_sections_mask >> (i * 4)) & 0xF
                if sec_idx < len(courses[i].sections):
                    temp_schedule.add_section(courses[i].sections[sec_idx])
            temp_schedule.add_section(section)
            
            # Skip if this creates conflicts
            if temp_schedule.has_conflicts():
                continue
            
            # Recursive call for next course
            score, selection = solve(course_idx + 1, new_mask)
            
            if score > best_score:
                best_score = score
                best_selection = selection.copy()
                best_selection[course_idx] = section_idx
        
        dp[(course_idx, selected_sections_mask)] = best_score
        selections[(course_idx, selected_sections_mask)] = best_selection
        return best_score, best_selection
    
    # Start solving from first course with empty mask
    final_score, final_selections = solve(0, 0)
    
    # Build the schedule from selections
    final_schedule = Schedule()
    for course_idx, section_idx in final_selections.items():
        final_schedule.add_section(courses[course_idx].sections[section_idx])
    
    final_schedule.score = final_score
    return final_schedule

def backtracking_scheduler(courses, preferences):
    """Find optimal schedule using backtracking"""
    best_schedule = Schedule()
    best_schedule.score = float('-inf')
    
    def backtrack(course_idx, current_schedule):
        nonlocal best_schedule
        
        # Base case: all courses processed
        if course_idx == len(courses):
            score = current_schedule.calculate_score(preferences)
            if score > best_schedule.score:
                # Create a new schedule object to avoid reference issues
                best_schedule = Schedule()
                for section in current_schedule.assigned_sections:
                    best_schedule.add_section(section)
                best_schedule.score = score
            return
        
        # Try each section of current course
        for section in courses[course_idx].sections:
            # Add this section temporarily
            current_schedule.add_section(section)
            
            # Only proceed if no conflicts
            if not current_schedule.has_conflicts():
                # Estimate the upper bound of potential score
                potential_score = current_schedule.calculate_score(preferences)
                
                # Only continue exploration if there's potential to improve best score
                if potential_score > best_schedule.score:
                    backtrack(course_idx + 1, current_schedule)
            
            # Remove the section (backtrack)
            current_schedule.assigned_sections.pop()
    
    # Start backtracking from first course with empty schedule
    backtrack(0, Schedule())
    return best_schedule

def main():
    # Create sample courses and sections
    courses = []
    
    # CS101 - Intro to Programming
    cs101 = Course("CS101", "Intro to Programming")
    cs101.add_section(Section("1", "CS101", [0, 2], 9*60, 10*60+30, "Smith"))  # MW 9:00-10:30
    cs101.add_section(Section("2", "CS101", [1, 3], 11*60, 12*60+30, "Johnson"))  # TTh 11:00-12:30
    cs101.add_section(Section("3", "CS101", [0, 2, 4], 14*60, 15*60, "Davis"))  # MWF 2:00-3:00
    courses.append(cs101)
    
    # CS201 - Data Structures
    cs201 = Course("CS201", "Data Structures")
    cs201.add_section(Section("1", "CS201", [0, 2], 11*60, 12*60+30, "Wilson"))  # MW 11:00-12:30
    cs201.add_section(Section("2", "CS201", [1, 3], 9*60, 10*60+30, "Brown"))  # TTh 9:00-10:30
    cs201.add_section(Section("3", "CS201", [2, 4], 15*60, 16*60+30, "Taylor"))  # WF 3:00-4:30
    courses.append(cs201)
    
    # MATH101 - Calculus I
    math101 = Course("MATH101", "Calculus I")
    math101.add_section(Section("1", "MATH101", [0, 2, 4], 8*60, 9*60, "Garcia"))  # MWF 8:00-9:00
    math101.add_section(Section("2", "MATH101", [1, 3], 13*60, 14*60+30, "Miller"))  # TTh 1:00-2:30
    math101.add_section(Section("3", "MATH101", [0, 4], 16*60, 17*60+30, "Anderson"))  # MF 4:00-5:30
    courses.append(math101)
    
    # PHYS101 - Physics I
    phys101 = Course("PHYS101", "Physics I")
    phys101.add_section(Section("1", "PHYS101", [1, 3], 15*60, 16*60+30, "Thomas"))  # TTh 3:00-4:30
    phys101.add_section(Section("2", "PHYS101", [0, 2], 10*60, 11*60+30, "Martin"))  # MW 10:00-11:30
    phys101.add_section(Section("3", "PHYS101", [2, 4], 13*60, 14*60+30, "Jackson"))  # WF 1:00-2:30
    courses.append(phys101)
    
    # Create sample student preferences
    preferences = StudentPreferences()
    preferences.no_morning_weight = 10       # Strong preference for no morning classes
    preferences.free_days_weight = 8         # Strong preference for free days
    preferences.early_dismissal_weight = 6   # Moderate preference for early dismissal
    preferences.consecutive_classes_weight = 3  # Low preference for consecutive classes
    preferences.long_breaks_weight = 7       # High preference for long breaks
    
    preferences.preferred_earliest_time = 10 * 60  # No classes before 10 AM
    preferences.preferred_latest_time = 17 * 60    # No classes after 5 PM
    preferences.preferred_break_time = 60          # Prefer 1 hour breaks
    
    # Run the greedy algorithm
    greedy = greedy_schedule_optimizer(courses, preferences)
    dynamic = dynamic_programming_scheduler(courses, preferences)
    backtracking = backtracking_scheduler(courses, preferences)
    print("\nGreedy Algorithm Schedule:")
    greedy.print_schedule()
    print("\nDynamic Programming Schedule:")
    dynamic.print_schedule()
    print("\nBacktracking Schedule:")
    backtracking.print_schedule()
    
if __name__ == "__main__":
    main()
