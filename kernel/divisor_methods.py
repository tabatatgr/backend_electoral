from decimal import Decimal, getcontext
getcontext().prec = 28

def dhondt_divisor(total_seats, votes):
    """
    Método de divisores D'Hondt para asignar escaños.
    :param total_seats: número total de escaños a repartir (int)
    :param votes: dict {partido: votos}
    :return: dict {partido: escaños}
    """
    # Si no hay votos válidos o no hay escaños que asignar, retornar dict vacío
    if not votes or total_seats <= 0:
        return {}
    
    seats = {p: 0 for p in votes}
    quotients = {p: Decimal(v) for p, v in votes.items()}
    
    for _ in range(total_seats):
        # Encuentra el partido con el mayor cociente (solo si hay partidos)
        if not quotients:
            break
        max_party = max(quotients, key=lambda p: (quotients[p], p))
        seats[max_party] += 1
        # Actualiza el cociente de ese partido
        seats_so_far = seats[max_party]
        quotients[max_party] = Decimal(votes[max_party]) / (seats_so_far + 1)
    return seats
