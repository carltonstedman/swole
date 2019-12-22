# -*- coding: utf-8 -*-
"""Tool to load program from YAML and print out progression for lifting."""
from __future__ import absolute_import, division, print_function

from dataclasses import dataclass
from typing import Any, Iterable, List, Optional, Mapping, Union, Sequence, Text, TextIO

# third party
import yaml

from contracts import check, contract, new_contract  # type: ignore


# TYPES ##########

Numeric = Union[float, int]
ProgramData = Sequence[Mapping[str, Any]]


# CONTRACTS ##########

new_contract('program_data', 'seq(map(str: *))')


# DATA CLASSES ##########


@dataclass(frozen=True)
class WorkingSet:
    percent: float
    reps: int

    # optional
    amrap: bool = False

    def calculate_weight(self, tm: Optional[Numeric] = None, rounding: Optional[Numeric] = None) -> Numeric:
        """Calculate weight based on optional training max.

        >>> WorkingSet(percent=0.5, reps=10).calculate_weight()
        0.5

        >>> WorkingSet(percent=0.5, reps=10).calculate_weight(205, 10.0)
        100.0
        """
        return mround(float(tm) * self.percent, rounding) if tm else self.percent

    def stringify(self, tm: Optional[Numeric] = None, rounding: Optional[Numeric] = None) -> Text:
        """Pretty-print string representation for working set with optional training max.

        >>> WorkingSet(percent=0.5, reps=10).stringify()
        '0.5 x 10'

        >>> WorkingSet(amrap=True, percent=0.5, reps=10).stringify(215, 10.0)
        '100.0 x 10+'
        """
        weight = self.calculate_weight(tm, rounding=rounding)
        reps = f'{self.reps}+' if self.amrap else self.reps
        return f'{weight:.1f} x {reps}'


@dataclass(frozen=True)
class Session:
    __slots__ = ('name', 'sets')
    name: str
    sets: List[WorkingSet]


@dataclass(frozen=True)
class MicroCycle:
    __slots__ = ('name', 'sessions')
    name: str
    sessions: List[Session]


@dataclass(frozen=True)
class MesoCycle:
    name: str
    micros: List[MicroCycle]

    # optional
    tm_inc: Numeric = 0

    def effective_tm(self, tm: Optional[Numeric] = None) -> Optional[Numeric]:
        """Get effective training max for this mesocycle.

        >>> MesoCycle('m1', []).effective_tm(100)
        100.0

        >>> MesoCycle('m1', [], tm_inc=5).effective_tm(100)
        105.0
        """
        return float(tm) + float(self.tm_inc) if tm else None


@dataclass(frozen=True)
class Program:
    __slots__ = ('mesos', 'name')
    name: str
    mesos: List[MesoCycle]

    def present(self, rounding: Optional[Numeric] = None, tm: Optional[int] = None) -> None:
        """Pretty print program."""
        header = '=' * max(20, len(self.name))
        print(header, self.name, header)
        flattened = ((s, u, m) for m in self.mesos for u in m.micros for s in u.sessions)
        for session, micro, meso in flattened:
            flattened_name = '.'.join([meso.name, micro.name, session.name]).upper()
            banner = '-' * min(10, len(flattened_name))

            etm = meso.effective_tm(tm)
            if tm:
                print(banner, flattened_name, f'[TM: {etm}]', banner)
            else:
                print(banner, flattened_name, banner)

            for ws in session.sets:
                print(ws.stringify(meso.effective_tm(tm), rounding))

    def present_table(self, rounding: Optional[Numeric] = None, tm: Optional[int] = None) -> None:
        """Pretty print program as tabular data."""
        try:
            from tabulate import tabulate
        except ImportError:
            raise ImportError('Need to pip install tabulate!')

        header = '=' * max(20, len(self.name))
        print(header, self.name, header)

        for meso in self.mesos:
            headers: List[str] = []
            table: List[List[str]] = []
            for micro_number, micro in enumerate(meso.micros):
                headers.append('.'.join([meso.name, micro.name]))
                for session_number, session in enumerate(micro.sessions):
                    value = '\n'.join(ws.stringify(meso.effective_tm(tm), rounding) for ws in session.sets)
                    if len(table) <= session_number:
                        table.append([])
                    if len(table[session_number]) <= micro_number:
                        table[session_number].append(value)
                    else:
                        table[session_number][micro_number] = value
            print(tabulate(table, headers=headers, tablefmt='grid'))


# PUBLIC FUNCTIONS ##########


@contract(mesos='program_data')
def generate_mesos(mesos: ProgramData) -> Iterable[MesoCycle]:
    """Generate mesocycles from data."""
    for meso in mesos:
        micros = [micro for micro in generate_micros(meso['micros'])]
        options = {k: v for k, v in meso.items() if k in ('tm_inc',)}
        yield MesoCycle(meso['name'], micros, **options)


@contract(micros='program_data')
def generate_micros(micros: ProgramData) -> Iterable[MicroCycle]:
    """Generate microcycles from data."""
    for micro in micros:
        sessions = [session for session in generate_sessions(micro['sessions'])]
        yield MicroCycle(micro['name'], sessions)


@contract(sessions='program_data')
def generate_sessions(sessions: ProgramData) -> Iterable[Session]:
    """Generate sessions from data."""
    for session in sessions:
        workingsets = [ws for ws in generate_workingsets(session['sets'])]
        yield Session(session['name'], workingsets)


@contract(workingsets='program_data')
def generate_workingsets(workingsets: ProgramData) -> Iterable[WorkingSet]:
    """Generate workingsets from data for session."""
    for ws in workingsets:
        workingset = WorkingSet(amrap=ws.get('amrap', False), percent=ws['percent'], reps=ws['reps'])
        for _ in range(ws.get('sets', 1)):
            yield workingset


def load_program(handle: TextIO) -> Program:
    """Load program from YAML file handle."""
    program: Mapping[str, Any] = yaml.safe_load(handle)
    check('map(str: str|program_data)', program)
    mesos = [meso for meso in generate_mesos(program['mesos'])]
    return Program(program['name'], mesos)


def mround(value: Numeric, rounding: Optional[Numeric] = None) -> Numeric:
    """Round to nearest rounding value.

    >>> mround(103, 2.5)
    102.5
    """
    if not rounding:
        rounding = 5.0
    return (float(value) // rounding) * rounding
