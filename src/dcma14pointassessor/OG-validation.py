import inspect
import datetime as dt

class Validation:
    def __init__(self, clean_data):
        self.data = clean_data


    # Validation Data Collector
    def create_error_record(
        self, record: dict, validation_info: dict, message: str
    ) -> dict:  # Move this out to the main scope to be used for all Validation Checks
        """Record is a dictionary with the following fields: TaskId, TaskIndex,TaskName.
        This is the coverented data that comes out of the Tasks API.
        validation_info is a dictionary with the following fields: Id,Name,Description.
        """
        output = {
            "ValidationId": validation_info["Id"],
            "ValidationName": validation_info["Name"],
            "ValidationType": validation_info["Type"],
            "TaskId": record["TaskId"],
            "TaskIndex": record["TaskIndex"],
            "TaskName": record["TaskName"],
            "Error": message,
        }
        return output


    # Check 1
    def _check_1_missing_logic(self, data: dict) -> list:

        def find_first_non_summary_task(
            task_list: dict,
        ) -> str:  # Need to rewrite this entirely
            min_date = None
            first_tasks = []
            for i in task_list.values():
                start_date = i["TaskStartDate"]
                summary = i["TaskIsSummary"]
                if not summary:
                    if min_date == None:
                        first_tasks = [i]
                        min_date = start_date
                    else:
                        if start_date < min_date:
                            min_date = start_date
                            first_tasks = [i]
                        elif start_date == min_date:
                            first_tasks.append(i)
            return [i["TaskId"] for i in first_tasks]

        # Validation Info
        validation_info = {
            "Id": 1,
            "Name": "Missing Logic",
            "Type": "Error",
            "Description": "Ensure that every task has at least one predecessor "\
                "and one successor. Exceptions are the starting task in the project "\
                "(which should only have a successor) and the finishing task of a project "\
                "(which should only have a predecessor). Milestones should also "\
                "only have predecessors and should not be used to drive activities.",
        }

        # Get My Data
        tasks = data["Tasks"]
        tasklinks = data["TaskLinks"]
        first_task_id = find_first_non_summary_task(tasks)

        output = []
        # Multiple First Tasks
        if len(first_task_id) > 1:
            for index, i in enumerate(first_task_id):
                output.append(
                    self.create_error_record(
                        record=tasks[i],
                        validation_info=validation_info,
                        message=f"This task is {index + 1} of {len(first_task_id)} "\
                        "which start the Schedule. The Schedule should start with a single task.",
                    )
                )

        for i in tasks.values():
            preds = len(
                list(filter(lambda x: x["SuccessorTaskId"] == i["TaskId"], tasklinks))
            )
            succs = len(
                list(filter(lambda x: x["PredecessorTaskId"] == i["TaskId"], tasklinks))
            )

            # Summary Task
            if i["TaskIsSummary"]:
                if preds > 0 or succs > 0:
                    # Message: Summary with Logic
                    output.append(
                        self.create_error_record(
                            record=i,
                            validation_info=validation_info,
                            message="Summary Task with Logic.",
                        )
                    )
            # Milestone Task
            elif i["TaskIsMilestone"]:
                if succs == 0 and preds == 0:
                    # Message: Milestone with no logic
                    output.append(
                        self.create_error_record(
                            record=i,
                            validation_info=validation_info,
                            message="Milestone Task with No Logic",
                        )
                    )
                elif succs > 0 and preds == 0 and i["TaskId"] not in first_task_id:
                    # Message: Milestone with Successors but no Predecessors
                    output.append(
                        self.create_error_record(
                            record=i,
                            validation_info=validation_info,
                            message="Milestone with Successors but no Predecessors.",
                        )
                    )
            # Regular Task
            else:
                if succs == 0 and preds == 0:
                    # Message: Task With no Logic
                    output.append(
                        self.create_error_record(
                            record=i,
                            validation_info=validation_info,
                            message="Task With no Logic.",
                        )
                    )
                elif succs > 0 and preds == 0 and i["TaskId"] not in first_task_id:
                    # Message: Task with Successors but no Predecessors
                    output.append(
                        self.create_error_record(
                            record=i,
                            validation_info=validation_info,
                            message="Task with Successors but no Predecessors.",
                        )
                    )
                elif succs == 0 and preds > 0:
                    # Message: Task with Predecessor bit to Successors
                    output.append(
                        self.create_error_record(
                            record=i,
                            validation_info=validation_info,
                            message="Task with Predecessors but no Successors.",
                        )
                    )

        # Result
        bad = len(output)
        total = len(tasks) - 1
        if total == 0:
            result = "N/A"
            summary = "You have 0 Tasks in this project schedule."
        else:
            if bad > 0:
                result = "Fail"
            else:
                result = "Pass"
            summary = f"You have {bad} of {total} tasks with bad logic."

        # Validation Info - Summary
        validation_info["Summary"] = summary
        validation_info["Result"] = result
        validation_info["Data"] = output
        return validation_info


    # Check 2: Leads
    def _check_2_leads(self, data: dict) -> list:
        # Validation Info
        validation_info = {
            "Id": 2,
            "Name": "Leads",
            "Type": "Error",
            "Description": "Remove all leads (AKA negative lags) from the schedule. "\
                "This may involve breaking down the predecessor task into two distinct "\
                "tasks in order to capture when the task with a lead should begin.",
        }
        output = []
        for i in data["TaskLinks"]:
            if i["LinkLag"] < 0:
                task_id = i["SuccessorTaskId"]
                error_message = (
                    "The Relationship to the Predecessor is a Lead (Negative Lag)."
                )
                output.append(
                    self.create_error_record(
                        record=data["Tasks"][task_id],
                        validation_info=validation_info,
                        message=error_message,
                    )
                )

        # Result
        bad = len(output)
        total = len(data["TaskLinks"])
        if total > 0:
            if bad > 0:
                result = "Fail"
            else:
                result = "Pass"
            summary = f"You have {bad} of {total} task relationships with leads."
        else:
            result = "N/A"
            summary = f"There are 0 Task Relationships in this project schedule."

        # Validation Info - Summary
        validation_info["Summary"] = (summary)
        validation_info["Result"] = result
        validation_info["Data"] = output
        return validation_info


    # Check 3: Lags
    def _check_3_lags(self, data: dict) -> list:
        # Validation Info
        validation_info = {
            "Id": 3,
            "Name": "Lags",
            "Type": "Warning",
            "Description": "Some lags are acceptable, but they need to be limited to less "\
                "than 5% of the total task relationships in the schedule. Review the lags that "\
                "exist and ensure they're minimized.",
        }
        output = []
        for i in data["TaskLinks"]:
            if i["LinkLag"] > 0:
                task_id = i["SuccessorTaskId"]
                error_message = "The Relationship to the Pred is a Lag."
                output.append(
                    self.create_error_record(
                        record=data["Tasks"][task_id],
                        validation_info=validation_info,
                        message=error_message,
                    )
                )

        # Result
        bad = len(output)
        total = len(data["TaskLinks"])
        if total > 0:
            if bad / total > 0.05:
                result = "Fail"
            else:
                result = "Pass"
            summary = f"You have {format(bad/total,'0.2%')} ({bad} of {total}) task relationships with lags."
        else:
            result = "N/A"
            summary = f"You have 0 Task Relationships in this project schedule."

        # Validation Info - Summary
        validation_info["Summary"] = (summary)
        validation_info["Result"] = result
        validation_info["Data"] = output
        return validation_info


    # Check 4: Hard Start Contraints
    def _check_4_hard_start_constraints(self, data: dict) -> list:
        """Checks for Constraint Types 3,5,6"""

        # Validation Info
        validation_info = {
            "Id": 4,
            "Name": "Hard Start Constraints",
            "Type": "Warning",
            "Description": "Hard start constraints should be used sparingly. "\
                "While they are sometimes necessary, the vast majority of tasks should "\
                "be driven by logic rather than a constraint date.",
        }

        CONTRAINT_TYPES = {
            1: "As Soon As Possible",
            2: "As Late As Possible",
            3: "Must Start On",
            4: "Must Finish On",
            5: "Start No Earlier Than",
            6: "Start No Later Than",
            7: "Finish No Earlier Than",
            8: "Finish No Later Than",
        }

        output = []
        for i in data["Tasks"].values():
            ct = i["ConstraintType"]
            if ct in (3, 5, 6):
                output.append(
                    self.create_error_record(
                        record=i,
                        validation_info=validation_info,
                        message=f"This Task has a Hard Start Constraint: {CONTRAINT_TYPES[ct]}",
                    )
                )

        # Result
        bad = len(output)
        total = len(data["Tasks"]) - 1
        if total == 0:
            result = "N/A"
            summary = f"You have 0 Tasks in this project schedule."
        else:
            if bad / total > 0.05:
                result = "Fail"
            else:
                result = "Pass"
            summary = f"You have {format(bad/total,'0.2%')} ({bad} of {total}) tasks with Hard Start Constraints."

        # Validation Info - Summary
        validation_info["Summary"] = (summary)
        validation_info["Result"] = result
        validation_info["Data"] = output
        return validation_info


    # Check 5: Hard Start Contraints
    def _check_5_hard_finish_constraints(self, data: dict) -> list:
        """Checks for Constraint Types 4,7,8"""
        # Validation Info
        validation_info = {
            "Id": 5,
            "Name": "Hard Finish Constraints",
            "Type": "Error",
            "Description": "A task should never be forced to finsh on a certain day. "\
                "If the logic in a schedule is sound, the finish dates shown are realistic "\
                "and work needs to be planned differently to pull in a shown finish date.",
        }

        CONTRAINT_TYPES = {
            1: "As Soon As Possible",
            2: "As Late As Possible",
            3: "Must Start On",
            4: "Must Finish On",
            5: "Start No Earlier Than",
            6: "Start No Later Than",
            7: "Finish No Earlier Than",
            8: "Finish No Later Than",
        }

        output = []
        for i in data["Tasks"].values():
            ct = i["ConstraintType"]
            if ct in (4, 7, 8):
                output.append(
                    self.create_error_record(
                        record=i,
                        validation_info=validation_info,
                        message=f"This Task has a Hard Finish Constraint: {CONTRAINT_TYPES[ct]}",
                    )
                )

        # Result
        bad = len(output)
        total = len(data["Tasks"]) - 1
        if total == 0:
            result = "N/A"
            summmary = f"You have 0 Tasks in this project schedule."
        else:
            if bad > 0:
                result = "Fail"
            else:
                result = "Pass"
            summmary = f"You have {bad} of {total} tasks with Hard Finish Constraints."

        # Validation Info - Summary
        validation_info["Summary"] = (summmary)
        validation_info["Result"] = result
        validation_info["Data"] = output
        return validation_info


    # Check 6: High Duration Tasks
    def _check_6_high_duration_tasks(self, data: dict) -> list:
        """Checks TaskDuration for more than 320 hours (40 Days)"""

        # Validation Info
        validation_info = {
            "Id": 6,
            "Name": "High Duration Tasks",
            "Type": "Warning",
            "Description": "Tasks with durations over 40 days should be limited. "\
                "Generally, long tasks should be broken down into multiple, shorter "\
                "tasks in order to increase schedule fidelity.",
        }

        output = []
        for i in data["Tasks"].values():
            if i["TaskDuration"] >= 320 and not i["TaskIsSummary"]:
                output.append(
                    self.create_error_record(
                        record=i,
                        validation_info=validation_info,
                        message=f"This Task's duration of {i['TaskDuration']/8} Days is more than 40 Days",
                    )
                )

        # Result
        bad = len(output)
        total = len(
            list(filter(lambda x: x["TaskIsSummary"] is not True, data["Tasks"].values()))
        )
        if total == 0:
            result = "N/A"
            summary = f"You have 0 Non-Summary Tasks in this project schedule."
        else:
            if bad / total > 0.05:
                result = "Fail"
            else:
                result = "Pass"
            summary = f"You have {format(bad/total,'0.2%')} ({bad} of {total}) tasks with Duration over 40 Days."

        # Validation Info - Summary
        validation_info["Summary"] = (summary)
        validation_info["Result"] = result
        validation_info["Data"] = output
        return validation_info


    # Check 7: Invalid Dates
    def _check_7_invalid_dates(self, data: dict) -> list:
        """Checks if the Actual Start or Finish Dates are Greater than the Project Status Date."""

        # Validation Info
        validation_info = {
            "Id": 7,
            "Name": "Invalid Actual Dates",
            "Type": "Error",
            "Description": "A task with an invalid date is showing an actual start or "\
                "an actual finish date that is after the status date of the file. "\
                "Ensure that the status date is accurate, then ensure that no tasks are "\
                "started or finished in the future.",
        }

        status_date_available = None
        output = []
        if data["ProjectStatusDate"] is not None:
            status_date_available = True
            for i in data["Tasks"].values():
                status_date = data["ProjectStatusDate"]
                actual_start = i["TaskActualStartDate"]
                actual_finish = i["TaskActualFinishDate"]
                if actual_start is not None and actual_finish is not None:
                    if actual_start > status_date:
                        output.append(
                            self.create_error_record(
                                record=i,
                                validation_info=validation_info,
                                message=f"Task Actual Start Date ({actual_start.date()}) "\
                                    f"is after the Project Status Date ({status_date.date()}).",
                            )
                        )
                    elif actual_finish > status_date:
                        output.append(
                            self.create_error_record(
                                record=i,
                                validation_info=validation_info,
                                message=f"Task Actual Finish Date ({actual_finish.date()}) "\
                                    f"is after the Project Status Date ({status_date.date()}).",
                            )
                        )
                elif actual_start is not None:
                    if actual_start > status_date:
                        output.append(
                            self.create_error_record(
                                record=i,
                                validation_info=validation_info,
                                message=f"Task Actual Start Date ({actual_start.date()}) "\
                                    f"is after the Project Status Date ({status_date.date()}).",
                            )
                        )
                elif actual_finish is not None:
                    if (
                        actual_finish > status_date
                    ):  # THis was missing before. Why? Review this logic.
                        output.append(
                            self.create_error_record(
                                record=i,
                                validation_info=validation_info,
                                message=f"Task Actual Finish Date ({actual_finish.date()}) "\
                                    f"is after the Project Status Date ({status_date.date()}).",
                            )
                        )
        else:
            status_date_available = False

        # Result
        bad = len(output)
        total = len(data["Tasks"]) - 1

        if total == 0:
            result = "N/A"
            summary = "You have 0 Tasks in this project schedule."
        else:
            if status_date_available:
                summary = f"You have {bad} of {total} tasks with with the Actual Start Date or "\
                    f"Actual Finish Date which is greater than the Project Status Date ({status_date.date()})"
                if bad > 0:
                    result = "Fail"
                else:
                    result = "Pass"
            else:
                summary = f"The Project Status Date has not been entered."
                result = "Fail"

        # Validation Info - Summary
        validation_info["Summary"] = summary
        validation_info["Result"] = result
        validation_info["Data"] = output
        return validation_info


    # Check 8: Project Status Date
    def _check_8_project_status_date(self, data: dict) -> list:
        """Checks the Status Date vs the Last Published Date."""

        # Validation Info
        validation_info = {
            "Id": 8,
            "Name": "Project Status Date",
            "Type": "Warning",
            "Description": "Projects in our web environment need to be updated at "\
                "least monthly with a new status date and new progress reported. "\
                "Ensure that schedules are being updated with a new status date and "\
                "ensure that the file is published.",
        }

        fake_record = {
            "TaskId": "N/A",
            "TaskIndex": "Project",
            "TaskName": data["ProjectName"],
        }

        status_date = data.get("ProjectStatusDate")
        published_date = data["ProjectLastPublishedDate"]

        days = 15
        output = []
        if status_date is None:
            output.append(
                self.create_error_record(
                    record=fake_record,
                    validation_info=validation_info,
                    message="There is no Status Date set for this Project.",
                )
            )
        elif abs((published_date - status_date).days) > days:
            output.append(
                self.create_error_record(
                    record=fake_record,
                    validation_info=validation_info,
                    message=f"The Project Status Date {status_date.date()} is more than "\
                    f"{days} days from the Last Published Date {published_date.date()}",
                )
            )
        elif status_date.date() > published_date.date():
            output.append(
                self.create_error_record(
                    record=fake_record,
                    validation_info=validation_info,
                    message=f"The Project Status Date ({status_date.date()}) "\
                    f"is after the Last Published Date ({published_date.date()}).",
                )
            )

        # Result
        bad = len(output)
        if bad > 0:
            result = "Fail"
            summary = output[0]["Error"]
        else:
            result = "Pass"
            summary = f"The Project Status Date ({status_date.date()}) is "\
            f"Valid and within {days} days of the Last Published Date ({published_date.date()})."

        # Validation Info - Summary
        validation_info["Summary"] = summary
        validation_info["Result"] = result
        validation_info["Data"] = output
        return validation_info


    # Check 9: Phase
    def _check_9_phase(self, data: dict) -> list:
        """This function checks that any task with Phase Not Null is a Summary Task."""

        # Validation Info
        validation_info = {
            "Id": 9,
            "Name": "Phase",
            "Type": "Error",
            "Description": 'The "Phase" dropdown should only be used on summary tasks. '\
                "Ensure that non-summary tasks do not have a phase listed.",
        }

        output = []
        for i in data["Tasks"].values():
            if i["Phase"] is not None and not i["TaskIsSummary"]:
                output.append(
                    self.create_error_record(
                        record=i,
                        validation_info=validation_info,
                        message="The Phase column should only be used for Summary Tasks.",
                    )
                )

        # Result
        bad = len(output)
        total = len(data["Tasks"]) - 1
        if total == 0:
            result = "N/A"
            summary = f"You have 0 Tasks in this project schedule."
        else:
            if bad > 0:
                result = "Fail"
            else:
                result = "Pass"
            summary = f"You have {bad} task(s) with incorrect Phase(Enterprise) values."

        # Validation Info - Summary
        validation_info["Summary"] = (summary)
        validation_info["Result"] = result
        validation_info["Data"] = output
        return validation_info


    # Check 10: Reporting
    def _check_10_Reporting(self, data: dict) -> list:
        """Checks Tasks to make sure the Reporting Fields are set properly."""

        # Validation Info
        validation_info = {
            "Id": 10,
            "Name": "Reporting",
            "Type": "Error",
            "Description": 'The "Reporting" field contains distinct options for '\
                'milestones and tasks. Ensure that the correct option is '\
                'selected for each of these task types.',
        }

        output = []
        for i in data["Tasks"].values():
            if i["Reporting"] is not None:
                if i["TaskIsMilestone"] and i["ReportingDescription"] != "Milestone Flag":
                    output.append(
                        self.create_error_record(
                            record=i,
                            validation_info=validation_info,
                            message='Incorrect Reporting Value for Milestone Tasks. '\
                            'Please only use values with description "Milestone Flag".',
                        )
                    )
                elif (
                    not i["TaskIsMilestone"]
                    and not i["TaskIsSummary"]
                    and i["ReportingDescription"] != "Task"
                ):
                    output.append(
                        self.create_error_record(
                            record=i,
                            validation_info=validation_info,
                            message='Incorrect Reporting Value for Tasks. '\
                                'Please only use values with description "Task".',
                        )
                    )
                elif i["TaskIsSummary"]:
                    output.append(
                        self.create_error_record(
                            record=i,
                            validation_info=validation_info,
                            message="Summary Tasks should not have Reporting "\
                                "Values Assigned.",
                        )
                    )

        # Result
        bad = len(output)
        total = len(data["Tasks"]) - 1
        if total == 0:
            result = "N/A"
            summary = f"You have 0 Tasks in this project schedule."
        else:
            if bad > 0:
                result = "Fail"
            else:
                result = "Pass"
            summary = f"You have {bad} task(s) with incorrect Reporting(Enterprise) values."

        # Validation Info - Summary
        validation_info["Summary"] = (summary)
        validation_info["Result"] = result
        validation_info["Data"] = output
        return validation_info


    # Check 11: Phase & Reporting Mutually Exclusive
    def _check_11_phase_or_reporting(self, data: dict) -> list:
        """Checks for the existence of both the Phase and Reporting Fields."""

        # Validation Info
        validation_info = {
            "Id": 11,
            "Name": "Phase & Reporting Mutually Exclusive",
            "Type": "Error",
            "Description": "The Phase field is only filled out on summary tasks. "\
                "When a summary task has the phase field filled out, "\
                "it should not hae the supporting field filled out.",
        }

        output = []
        for i in data["Tasks"].values():
            if i["Reporting"] is not None and i["Phase"] is not None:
                output.append(
                    self.create_error_record(
                        record=i,
                        validation_info=validation_info,
                        message="The Phase and Reporting fields are mutually "\
                            "exclusive. Please only select the appropriate field to fill out.",
                    )
                )

        # Result
        bad = len(output)
        total = len(data["Tasks"]) - 1
        if total == 0:
            result = "N/A"
            summary = f"You have 0 Tasks in this project schedule."
        else:
            if bad > 0:
                result = "Fail"
            else:
                result = "Pass"
            summary = f"You have {bad} task(s) where both the Phase(Enterprise) and "\
                f"Reporting(Enterprise) fields contain values."

        # Validation Info - Summary
        validation_info["Summary"] = (summary)
        validation_info["Result"] = result
        validation_info["Data"] = output
        return validation_info


    # Check 12: Project Schedule Structure
    def _check_12_Project_Schedule_Structure(self, data: dict) -> list:
        """Checks the Project Structure to only have one Level 1 Task."""

        # Validation Info
        validation_info = {
            "Id": 12,
            "Name": "Schedule Structure",
            "Type": "Error",
            "Description": "A level 1 task is outdented to the maximum level. "\
                "There should only be one task at this level (which should "\
                "contain the name of the project) and all other tasks should "\
                "be nested under this task.",
        }

        output = []
        for i in data["Tasks"].values():
            if i["TaskOutlineLevel"] == 1 and i["TaskIndex"] != 1:
                output.append(
                    self.create_error_record(
                        record=i,
                        validation_info=validation_info,
                        message="There should only be one Level 1 Task(The "\
                            "first task) in the Project Schedule.",
                    )
                )

        # Result
        bad = len(output)
        total = len(data["Tasks"]) - 1
        if total == 0:
            result = "N/A"
            summary = f"You have 0 Tasks in this project schedule."
        else:
            if bad > 0:
                result = "Fail"
                summary = f"You have {bad} extra task(s) at the outer most indent level."
            else:
                result = "Pass"
                summary = "All Tasks are at the proper indent level."

        # Validation Info - Summary
        validation_info["Summary"] = summary
        validation_info["Result"] = result
        validation_info["Data"] = output
        return validation_info


    # Check 13: Missing Baselines
    def _check_13_baselines(self, data: dict) -> list:

        #Validation Info
        validation_info = {
            'Id': 13,
            'Name': 'Schedule Baseline Checks',
            'Type': 'Error',
            'Description': 'TBD'
        }

        fake_record = {
            'TaskId': 'N/A',
            'TaskIndex': 'Project',
            'TaskName': data['ProjectName'],
        }


        output = []
        # Baseline Data
        project_baselines = data['ProjectBaselines']
        project_baseline_numbers = [x['BaselineNumber'] for x in project_baselines]

        task_baselines = data['TaskBaselines']
        task_baseline_numbers = list(set([x['BaselineNumber'] for x in task_baselines]))

        # Check Project Baselines Exist #################
        if len(project_baselines) == 0 or len(task_baselines) == 0:
            output.append(
                self.create_error_record(
                    record=fake_record,
                    validation_info=validation_info,
                    message='There are no Project or Task Baseline Records. Please Set the Baseline on the schedule when ready.'
                )
            )
        # Check Project Baseline Numbers Match Between ##
        elif max(project_baseline_numbers) != max(task_baseline_numbers):
            output.append(
                self.create_error_record(
                    record=fake_record,
                    validation_info=validation_info,
                    message='There is an issue with the latest Baseline number. There are not matching records in both tables.'
                )
            )
        else:
            # Check if Each Baseline
            for id, record in data['Tasks'].items():
                if record['TaskIsActive']:
                    baseline_count = list(filter(lambda x: x['TaskId'] == id and x['BaselineNumber'] == max(task_baseline_numbers), task_baselines))
                    if baseline_count == 0:
                        output.append(
                            self.create_error_record(
                                record= record,
                                validation_info=validation_info,
                                message=f'This Task is missing a Task Baseline Record for the Latest Baseline Number: {max(task_baseline_numbers)}'
                            )
                        )

        # Result
        total = len(data["Tasks"]) - 1
        if total == 0:
            result = "N/A"
            summary = f"You have 0 Tasks in this project schedule."
        else:
            if len(output) == 0:
                result = 'Pass'
            else:
                result = 'Fail'
            summary = f'You have {len(output)} Baseline Issues to address.'

        # Validation Info - Summary
        validation_info['Summary'] = summary
        validation_info['Result'] = result
        validation_info['Data'] = output

        return validation_info

    # Check #14: Manually Scheduled Tasks
    def _check_14_manually_scheduled_tasks(self, data: dict) -> list:
        """Checks for Manually Scheduled Tasks."""

        # Validation Info
        validation_info = {
            "Id": 14,
            "Name": "Manually Scheduled Tasks",
            "Type": "Error",
            "Description": 'The mode for all tasks should be "Automatically Scheduled". '\
                'Manually scheduled tasks do not follow logic and should be switched to '\
                'automatic. Review the schedule after this fix, as it may cause dates to change.',
        }

        output = []
        for i in data["Tasks"].values():
            if i["TaskIsManuallyScheduled"]:
                output.append(
                    self.create_error_record(
                        record=i,
                        validation_info=validation_info,
                        message="Task is manually scheduled. There should be no Manually Scheduled Tasks.",
                    )
                )

        # Result
        bad = len(output)
        total = len(data["Tasks"]) - 1
        if total == 0:
            result = "N/A"
            summary = f"You have 0 Tasks in this project schedule."
        else:
            if bad > 0:
                result = "Fail"
                summary = f"You have {bad} Manually Scheduled task(s)."
            else:
                result = "Pass"
                summary = "All tasks are Automatically Scheduled."

        # Validation Info - Summary
        validation_info["Summary"] = summary
        validation_info["Result"] = result
        validation_info["Data"] = output
        return validation_info


    # Check 15: Relationships
    def _check_15_Relationships(self, data: dict) -> list:
        """Checks Relationship Types"""

        # Validation Info
        validation_info = {
            "Id": 15,
            "Name": "Non Finish to Start Relationships",
            "Type": "Warning",
            "Description": "Finish to Start is the standard relationships between tasks. "\
                "Start to Start or Finish to Finish relationships can be used sparingly, "\
                "but they should make up no more than 5% of the total task relationships.",
        }

        relationships = {
            0: "Finish to Finish",
            1: "Finish to Start",
            2: "Start to Finish",
            3: "Start to Start",
        }

        output = []
        for i in data["TaskLinks"]:
            if i["DependencyType"] != 1:
                task_id = i["SuccessorTaskId"]
                rel_type = i["DependencyType"]
                output.append(
                    self.create_error_record(
                        record=data["Tasks"][task_id],
                        validation_info=validation_info,
                        message=f"This tasks uses a {relationships[rel_type]} Relationship.",
                    )
                )

        # Result
        bad = len(output)
        total = len(data["TaskLinks"])
        if total == 0:
            result = "N/A"
            summary = f"You have 0 Tasks Relationships in this project schedule."
        else:
            if bad / total > 0.05:
                result = "Fail"
            else:
                result = "Pass"
            summary = f"You have {format(bad/total,'0.2%')} ({bad} of {total}) task "\
                    f"relationships with Non Finish to Start Relationships."

        # Validation Info - Summary
        validation_info["Summary"] = (summary)
        validation_info["Result"] = result
        validation_info["Data"] = output
        return validation_info


    # Check 16: Project Phases Structure
    def _check_16_project_phases_structure(self, data: dict) -> list:
        """Checks the Project Structure to make sure Project Phase tasks are only at Task Outline Level 2."""

        # Validation Info
        validation_info = {
            "Id": 16,
            "Name": "Project Phase Structure",
            "Type": "Error",
            "Description": "All Tasks marked with a Project Phase or Phase Zero " \
            "Phase field value should be indented to Task Outline Level 2.",
        }

        project_phases = ['Project Phase', 'Phase Zero']
        output = []
        for i in data["Tasks"].values():
            if i["Phase"] in project_phases and i["TaskOutlineLevel"] != 2:
                output.append(
                    self.create_error_record(
                        record=i,
                        validation_info=validation_info,
                        message=f'This task has a Phase value of "{i["Phase"]}" and is ' \
                        f'indented to Task Outline Level {i["TaskOutlineLevel"]}. ' \
                        f'Tasks with a Phase value of "{i["Phase"]}" should always be ' \
                        f'indented to Task Outline Level 2.',
                    )
                )

        # Result
        bad = len(output)
        total = len(data["Tasks"]) - 1
        if total == 0:
            result = "N/A"
            summary = f"You have 0 Tasks in this project schedule."
        else:
            if bad > 0:
                result = "Fail"
                summary = f"You have {bad} Project Phase task(s) at the wrong indent level."
            else:
                result = "Pass"
                summary = "All Project Phase Tasks are at the proper indent level."

        # Validation Info - Summary
        validation_info["Summary"] = summary
        validation_info["Result"] = result
        validation_info["Data"] = output
        return validation_info


# Function that Runs Functions to Do Validation #######################################################################
    def run_all_validations(self) -> dict:
        """Accepts project id and runs all Validation Check and produces a single output."""

        clean_data = self.data

        try:
            # Verification Checks
            verification_data = []
            verification_data.append(self._check_1_missing_logic(clean_data))
            verification_data.append(self._check_2_leads(clean_data))
            verification_data.append(self._check_3_lags(clean_data))
            verification_data.append(self._check_4_hard_start_constraints(clean_data))
            verification_data.append(self._check_5_hard_finish_constraints(clean_data))
            verification_data.append(self._check_6_high_duration_tasks(clean_data))
            verification_data.append(self._check_7_invalid_dates(clean_data))
            verification_data.append(self._check_8_project_status_date(clean_data))
            verification_data.append(self._check_9_phase(clean_data))
            verification_data.append(self._check_10_Reporting(clean_data))
            verification_data.append(self._check_11_phase_or_reporting(clean_data))
            verification_data.append(self._check_12_Project_Schedule_Structure(clean_data))
            verification_data.append(self._check_13_baselines(clean_data))
            verification_data.append(self._check_14_manually_scheduled_tasks(clean_data))
            verification_data.append(self._check_15_Relationships(clean_data))
            verification_data.append(self._check_16_project_phases_structure(clean_data))

            # Collect Output Data
            summary = []
            details = []
            timestamp = dt.datetime.now()
            project_info = {
                "Project Id": clean_data["ProjectId"],
                "Project Identifier": clean_data["ProjectIdentifier"],
                "Project Name": clean_data["ProjectName"],
                "Project Status": clean_data["ProjectStatus"],
                "Project Status Date": clean_data["ProjectStatusDate"],
                "Project Last Published Date": clean_data["ProjectLastPublishedDate"],
                "Project Owner Name": clean_data["ProjectOwnerName"],
                "Project Director": clean_data["ProjectDirector"],
                "Project Percent Complete": clean_data["ProjectPercentCompleted"],
                "Project Start Date": clean_data["ProjectStartDate"],
                "Project Finish Date": clean_data["ProjectFinishDate"],
                "Audit Timestamp": timestamp,
            }

            def supress_validation_type(result: str, val_type: str) -> str:
                if result == "Pass":
                    return None
                else:
                    return val_type

            for i in verification_data:
                summary.append(
                    {
                        "Result": i["Result"],
                        "#": i["Id"],
                        "Name": i["Name"],
                        "Type": supress_validation_type(i["Result"], i["Type"]),
                        "Description": i["Description"],
                        "Summary": i["Summary"],
                    }
                )
                details += i["Data"]

            # Output Info
            output = {
                "FileName": f"{timestamp.strftime('%Y-%m-%dT%H.%M.%S')}_-_"\
                    f"{clean_data['ProjectIdentifier']}_-_{clean_data['ProjectName']}.xlsx",
                "ProjectInfo": project_info,
                "Summary": summary,
                "Details": details
            }

            return {'Status': True, 'Function': inspect.currentframe().f_code.co_name,'Data': output, 'Message': None}

        except Exception as e:
            return {'Status': False, 'Function': inspect.currentframe().f_code.co_name,'Data': None, 'Message': e}
