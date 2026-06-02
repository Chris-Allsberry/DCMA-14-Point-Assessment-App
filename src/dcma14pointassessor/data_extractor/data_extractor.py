
import os
from dataclasses import dataclass
import datetime as dt
from pathlib import Path
import jpype
import jpype.imports
import mpxj

from .project_classes import ProjectData, ProjectProperties, Task, TaskRelation, ResourceAssignment, Duration

if not jpype.isJVMStarted():
    jpype.startJVM("-Dlog4j2.loggerContextFactory=org.apache.logging.log4j.simple.SimpleLoggerContextFactory") # Move this to the start of the app

from java.io import ByteArrayInputStream
from java.lang import Byte
from org.mpxj.reader import UniversalProjectReader


class DataExtractor:
    def __init__(self, filepath_or_bytes: str | bytes):
        self.file = self.__bytes_converter(filepath_or_bytes)
        self.project = UniversalProjectReader().read(self.file)


    def __bytes_converter(self, file: str | bytes):
        if type(file) == str:
            return file
        else:
            java_bytes = jpype.JArray(jpype.JByte)(file)
            input_stream = ByteArrayInputStream(java_bytes)
            return input_stream

    def __to_string(self, input) -> str | None:
        if input == None:
            return None
        else:
            try:
                return str(input.toString())
            except:
                return str(input)

    def __java_to_datetime(self, input) -> dt.datetime | None:
        if input == None:
            return None
        else:
            date_string = str(input.toString())
            date = dt.datetime.strptime(date_string, '%Y-%m-%dT%H:%M')
            return date

    def __str_to_datetime(self, input) -> dt.datetime | None:
        if input == None:
            return None
        else:
            date = dt.datetime.strptime(input, '%Y-%m-%dT%H:%M')
            return date

    def __to_datetime_from_iso(self, input):
        if input == None:
            return None
        else:
            return dt.datetime.fromisoformat(input)


    def __to_number(self, input) -> int | float | None:
        if input == None:
            return input
        else:
            try:
                return int(input)
            except:
                return float(input)


    def __get_duration(self, input) -> Duration:
        if input == None:
            return None
        else:
            return Duration(
                value=float(input.getDuration()),
                unit=str(input.getUnits().getName())
            )


    def __extract_project_properties(self) -> ProjectProperties:
        properties = self.project.getProjectProperties()
        status_string = self.__to_string(properties.getStatusDate())
        output = ProjectProperties(
            status_date=self.__str_to_datetime(status_string)
        )
        return output


    def __extract_tasks(self) -> list[Task]:
        output = []
        for task in self.project.getTasks():
            data = {
                "id": self.__to_number(task.getID()),
                "name": self.__to_string(task.getName()),
                "baseline_duration": self.__get_duration(task.getBaselineDuration()),
                "duration": self.__get_duration(task.getDuration()),
                "actual_duration": self.__get_duration(task.getActualDuration()),
                "baseline_start": self.__java_to_datetime(task.getBaselineStart()),
                "start": self.__java_to_datetime(task.getStart()),
                "actual_start": self.__java_to_datetime(task.getActualStart()),
                "baseline_finish": self.__java_to_datetime(task.getBaselineFinish()),
                "finish": self.__java_to_datetime(task.getFinish()),
                "actual_finish": self.__java_to_datetime(task.getActualFinish()),
                "baseline_work": self.__get_duration(task.getBaselineWork()),
                "work": self.__get_duration(task.getWork()),
                "actual_work": self.__get_duration(task.getActualWork()),
                "milestone": task.getMilestone(),
                "summary": task.getSummary(),
                "critical": task.getCritical(),
                "guid": self.__to_string(task.getGUID()),
                "resume": self.__java_to_datetime(task.getResume()), 
                "stop": self.__java_to_datetime(task.getStop()),
                'constraint_date' : self.__java_to_datetime(task.getConstraintDate()),
                'constraint_type' : self.__to_string(task.getConstraintType()),
                'active': task.getActive(),
                'task_mode': self.__to_string(task.getTaskMode()),
                'type': self.__to_string(task.getType()),
                'wbs': self.__to_string(task.getWBS()),
                'outline_level' : self.__to_number(task.getOutlineLevel()),
                'outline_number' : self.__to_string(task.getOutlineNumber()),
                'start_slack': self.__get_duration(task.getStartSlack()),
                'finish_slack': self.__get_duration(task.getFinishSlack()),
                'free_slack': self.__get_duration(task.getFreeSlack()),
                'total_slack': self.__get_duration(task.getTotalSlack()),
            }
            new_task = Task(**data)
            output.append(new_task)
        return output


    def __extract_task_relations(self):

        def get_relation_info(rel) -> TaskRelation:
            data = {
                        "lag": self.__get_duration(rel.getLag()),
                        "notes": self.__to_string(rel.getNotes()),
                        "predecessor": self.__to_string(rel.getPredecessorTask().getGUID()),
                        "successor": self.__to_string(rel.getSuccessorTask().getGUID()),
                        "type": self.__to_string(rel.getType()),
                        "uid": self.__to_number(self.__to_string(rel.getUniqueID()))
                    }
            return TaskRelation(**data)

        output = []
        for task in self.project.getTasks():
            for rel in task.getPredecessors():
                output.append(get_relation_info(rel))

        return output


    def __extract_resource_assignments(self) -> list[ResourceAssignment]:
        output = []
        for resource in self.project.getResources():
            for ra in resource.getTaskAssignments():
                data = { # Find Duration
                    'actual_finish': self.__java_to_datetime(ra.getActualFinish()),
                    'actual_start': self.__java_to_datetime(ra.getActualStart()),
                    'actual_work': self.__get_duration(ra.getActualWork()),
                    'baseline_finish': self.__java_to_datetime(ra.getBaselineFinish()),
                    'baseline_start': self.__java_to_datetime(ra.getBaselineStart()),
                    'baseline_work': self.__get_duration(ra.getBaselineWork()),
                    'create_date': self.__java_to_datetime(ra.getCreateDate()),
                    'delay': self.__get_duration(ra.getDelay()),
                    'finish': self.__java_to_datetime(ra.getFinish()),
                    'guid': self.__to_string(ra.getGUID()),
                    'resource': self.__to_string(ra.getResource().getName()),
                    'start': self.__java_to_datetime(ra.getStart()),
                    'task_guid': self.__to_string(ra.getTask().getGUID()),
                    'work': self.__get_duration(ra.getWork()),
                }
                new_ra = ResourceAssignment(**data)
                output.append(new_ra)
        return output

    def extract_data(self) -> ProjectData:
        project_properties = self.__extract_project_properties()
        tasks = self.__extract_tasks()
        task_relations = self.__extract_task_relations()
        resource_assignments = self.__extract_resource_assignments()
        return ProjectData(
            project_properties=project_properties,
            tasks=tasks,
            task_relations=task_relations,
            resource_assignments=resource_assignments
        )
