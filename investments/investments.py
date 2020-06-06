from flaskr.db import db


def create(user: str, principal: float, duration: int, portfolio: str):
    """
    Insert an investment into the DB.

    :param user:
    :param principal:
    :param duration:
    :param portfolio:
    """

    db_connection = db.get_db()
    db_connection.execute(
        f"""
        INSERT INTO investment (username, portfolio, duration, principal)
        VALUES ("{user}", "{portfolio}", {duration}, {principal})
        """)
    db_connection.commit()


def get(user: str):
    """
    Return the investments held by a given user.

    :param user:
    :return:
    """

    db_connection = db.get_db()

    i_raw = db_connection.execute(
        f"""
        SELECT id, portfolio, duration, principal 
        FROM investment
        WHERE username = "{user}" 
        ORDER BY id ASC
        """
    ).fetchall()

    investments = []

    for i_row in i_raw:
        investment = {
            'id': i_row[0],
            'portfolio': i_row[1],
            'duration': i_row[2],
            'principal': i_row[3]
        }

        investments.append(investment)

    if len(investments) == 0:
        return f"No investments for {user}"

    return investments


def suggest(principal: float, desired_risk: int, duration: int):
    """
    Calculate the minimum and maximum projected returns for a given principal
    sum and time frame against each investment portfolio in the system.
    Identify and recommend any which mach the given desired level of risk.

    :param principal: float
    :param desired_risk: int
    :param duration: int
    :return:
    """
    portfolios = Portfolios()
    projections = []
    for portfolio in portfolios.portfolios:
        returns = portfolio.project_returns(principal, duration)
        projection = {'Portfolio': portfolio.id,
                      'Minimum Return': returns['min'],
                      'Maximum Return': returns['max']}

        if portfolio.risk_level == desired_risk:
            projection['Recommended'] = True

        projections.append(projection)

    return projections


class Portfolio(object):
    def __init__(self, id: str, max_interest: float,
                 min_interest: float, risk_level: int):
        self.id = id
        self.max_interest = max_interest
        self.min_interest = min_interest
        self.risk_level = risk_level

    def project_returns(self, principal: float, duration: int):
        """
        Calculate the minimum and maximum projected returns for a given
        principal sum and time frame against this investment portfolio.

        :param principal: float
        :param duration: int
        :return:
        """
        return {'max': self._calculate_projection(principal,
                                                  duration,
                                                  self.max_interest),
                'min': self._calculate_projection(principal,
                                                  duration,
                                                  self.min_interest)}

    @staticmethod
    def _calculate_projection(principal: float, duration: int,
                              interest: float):
        """
        Apply the compound interest formula to a given principal sum,
        investment period, and interest rate.

        :param principal: float
        :param duration: int
        :param interest float
        :return:
        """
        return principal * ((1 + interest) ** duration)


class Portfolios(object):
    def __init__(self):
        self.portfolios = self.load_from_db()

    @staticmethod
    def load_from_db():
        """
        Load the data for investment portfolios from the database.
        """
        db_connection = db.get_db()

        pf_raw = db_connection.execute(
            'SELECT id, max, min, risk FROM portfolio ORDER BY id ASC'
        ).fetchall()

        portfolios = []
        for pf_row in pf_raw:
            portfolio = Portfolio(pf_row[0], pf_row[1], pf_row[2], pf_row[3])
            portfolios.append(portfolio)
        return portfolios
