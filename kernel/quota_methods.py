from decimal import Decimal
from math import floor

def largest_remainder_formula(quota, total_seats, votes):
    """
    Asigna escaños usando el método de restos mayores (LR-Hare, LR-Droop, etc).
    :param quota: cuota calculada (float o Decimal)
    :param total_seats: número total de escaños a repartir (int)
    :param votes: dict {partido: votos}
    :return: dict {partido: escaños}
    """
    seats = {}
    remainders = {}
    total_assigned = 0
    for party, v in votes.items():
        s = int(Decimal(v) // quota)
        seats[party] = s
        remainders[party] = Decimal(v) - s * quota
        total_assigned += s
    # Repartir los escaños restantes por restos mayores
    seats_left = total_seats - total_assigned
    if seats_left > 0:
        # Ordenar partidos por resto (descendente)
        sorted_parties = sorted(remainders.items(), key=lambda x: (-x[1], x[0]))
        for i in range(seats_left):
            party = sorted_parties[i][0]
            seats[party] += 1
    return seats

def hare_quota(total_seats, votes, total_votes):
    quota = Decimal(total_votes) / total_seats
    return largest_remainder_formula(quota, total_seats, votes)

def droop_quota(total_seats, votes, total_votes):
    quota = Decimal(1 + floor(Decimal(total_votes) / (total_seats + 1)))
    return largest_remainder_formula(quota, total_seats, votes)

def exact_droop_quota(total_seats, votes, total_votes):
    quota = Decimal(total_votes) / (total_seats + 1)
    assignment = largest_remainder_formula(quota, total_seats, votes)
    if sum(assignment.values()) > total_seats:
        return droop_quota(total_seats, votes, total_votes)
    else:
        return assignment
