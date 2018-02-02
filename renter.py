from copy import deepcopy
from datetime import date
from numpy import pmt, pv

BASEMENT_AREA = 904
GROUND_AREA = 756
FIRST_FLOOR_AREA = 740
TOTAL_AREA = 2400 # sqm
OPERATING_EXPENSE_INCREASE_RATE = 0.03
LEASING_COMMISSION_RATE = 0.05
CAPITAL_RESERVE_RATE = 2.26 # 2.26 euro per sqm
INITIAL_OPERATING_EXPENSE = 12.8*10.7639*2400
DEPOSIT = 5000000
PURCHASE_PRICE = 15000000

### LENDER A Constants ###
LENDER_A_LTV = 0.7
LENDER_A_INITIAL_TERM = 2 #years
LENDER_A_AMORTIZATION = 240 # months
LENDER_A_INTEREST_RATE = 0.05
LENDER_A_ENTRY_FEE = 0.01
LENDER_A_PER_EXTENSION_FEE = 0.005
LENDER_A_EXIT_FEE = 0.01

### Lender B Constants ###
LENDER_B_LTV = 0.6
LENDER_B_INITIAL_TERM = 5 #years
LENDER_B_AMORTIZATION = 240 # months
LENDER_B_INTEREST_RATE = 0.035
LENDER_B_ENTRY_FEE = 0.005
TREASURY_YIELD = 0.0014

"""
    Function: xirr
    ==============
    Compute xirr given the transaction in the format

        [(date1, cashflow1), (date2, cashflow2), ....]
"""
def xirr(transactions):
    years = [(ta[0] - transactions[0][0]).days / 365.0 for ta in transactions]
    residual = 1
    step = 0.05
    guess = 0.05
    epsilon = 0.0001
    limit = 10000
    while abs(residual) > epsilon and limit > 0:
        limit -= 1
        residual = 0.0
        for i, ta in enumerate(transactions):
            if pow(guess, years[i]) == 0: return None
            residual += ta[1] / pow(guess, years[i])
        if abs(residual) > epsilon:
            if residual > 0:
                guess += step
            else:
                guess -= step
                step /= 2.0
    return guess-1

"""
    class: Renter
    =============
    class Renter is a calculator for all essential figures affilitated with a specified renter
    This class requires 8 inputs

    1. name:                       Renter's name
    2. initialRentPerSqm           Initial rental per square meters (in euro)
    3. term                        How long the renter would like to stay (in year)
    4. annualIncrease              The annual increase rate for rent (decimal)
    5. isGuarantee                 boolean if the renter guarantee to complete the term
    6. abatement                   The number of months that the renter does not pay for the rent at the start of the contract
    7. ti                          Tenant Improvement (in euro per square meters)
    8. capRate                     Capital Rate for the tenant (decimal)
"""
class Renter(object):

    def __init__(self, name, initialRentPerSqm, term, annualIncrease, isGuarantee, abatement, ti, capRate):

        #### Initialization ####
        self.name = name
        self.initialRentPerSqm = initialRentPerSqm
        self.term = term
        self.isGuarantee = isGuarantee
        self.abatement = abatement
        self.annualIncrease = annualIncrease
        self.TI = ti*TOTAL_AREA
        self.capRate = capRate
        self.recompute()

    """ GET FUNCTIONS """
    def getName(self): return self.name
    def getInitialRentPerSqm(self): return self.initialRentPerSqm
    def getTerm(self): return self.term
    def getGuarantee(self): return self.isGuarantee
    def getAbatement(self): return self.abatement
    def getAnnualIncrease(self): return self.annualIncrease
    def getTI(self): return self.TI
    def getCapRate(self): return self.capRate
    def getOperatingExpense(self): return self.operatingExpense
    def getInitialAnnualRent(self): return self.initialAnnualRent
    def getBaseRentalRevenue(self): return self.baseRentalRevenue
    def getBaseRentalAbatement(self): return self.baseRentalAbatement
    def getScheduleBaseRentalRevenue(self): return self.scheduleBaseRentalRevenue
    def getTotalGrossRevenue(self): return self.totalGrossRevenue
    def getExpenseReimburseRevenue(self): return self.expenseReimburseRevenue
    def getNetOperatingIncome(self): return self.netOperatingIncome
    def getTotalLeasingAndCapitalCost(self): return self.totalLeasingAndCapitalCost
    def getCashFlowBeforeDebtService(self): return self.cashFlowBeforeDebtService

    """ SET FUNCTIONS """
    def setName(self, name):
        self.name = name
        if not name: self.recompute()

    def setInitialRentPerSqm(self, initialRentPerSqm):
        self.initialRentPerSqm = initialRentPerSqm
        self.recompute()

    def setTerm(self, term):
        self.term = term
        self.recompute()

    def setIsGuarantee(self, isGuarantee):
        self.isGuarantee = isGuarantee
        self.recompute()

    def setAbatement(self, abatement):
        self.abatement = abatement
        self.recompute()

    def setAnnualIncrease(self, annualIncrease):
        self.annualIncrease = annualIncrease
        self.recompute()

    def setTI(self, ti):
        self.TI = ti*TOTAL_AREA
        self.recompute()

    def setCapRate(self, capRate):
        self.capRate = capRate
        self.recompute()

    """
        class function: recompute
        =========================
        Recompute all essential figures related to cash flow before debt Service.
        This function should be called once any input variable is changed.
    """
    def recompute(self):
        ### Compute Net Operating Income
        self.initialAnnualRent = self.initialRentPerSqm * TOTAL_AREA
        self.baseRentalRevenue = [self.initialAnnualRent*((1 + self.annualIncrease) ** i) for i in xrange(self.term)]
        self.baseRentalAbatement = self.abatement/12.0*self.initialAnnualRent
        self.scheduleBaseRentalRevenue = deepcopy(self.baseRentalRevenue)
        self.scheduleBaseRentalRevenue[0] -= self.baseRentalAbatement
        self.operatingExpense = [INITIAL_OPERATING_EXPENSE * ((1 + OPERATING_EXPENSE_INCREASE_RATE)**i) for i in xrange(self.term)]
        if self.name is not None:
            self.expenseReimburseRevenue = deepcopy(self.operatingExpense)
        else:
            self.expenseReimburseRevenue = [0 for _ in xrange(self.term)]

        self.totalGrossRevenue = map(lambda x,y: x + y, self.scheduleBaseRentalRevenue, self.expenseReimburseRevenue)
        self.netOperatingIncome = map(lambda x,y: x - y, self.totalGrossRevenue, self.operatingExpense)

        ### Compute Cash Flow Before Debt Service
        self.leasingCommission = [self.baseRentalRevenue[0]*LEASING_COMMISSION_RATE*(1 + self.annualIncrease)**(i) for i in xrange(self.term)]
        self.capitalReserve = [TOTAL_AREA*CAPITAL_RESERVE_RATE for _ in xrange(self.term)]
        self.totalLeasingAndCapitalCost = deepcopy(self.capitalReserve)
        self.totalLeasingAndCapitalCost[0] += self.TI #+ self.leasingCommission
        self.totalLeasingAndCapitalCost = map(lambda x,y: x + y, self.totalLeasingAndCapitalCost, self.leasingCommission)
        self.cashFlowBeforeDebtService = map(lambda x,y: x - y, self.netOperatingIncome, self.totalLeasingAndCapitalCost)

"""
    function: getCashFlowUnleveraged
    ======================================
    Compute cash flow for unleveraged case. This function requires three input variables and one optional.

    cashFlowBeforeDebtService = cash flow before the debt of service (must be concat with empty period and match with the transation date in IRR computation)
    netOperatingIncome = net operating income (same as above)
    capRate = capital rate of the renter at the time that we exit
    yearExit = The beginning of the year that sells the building (Not recommended leave it none)
"""
def getCashFlowUnleveraged(cashFlowBeforeDebtService, netOperatingIncome, capRate, yearExit=None):
    cashFlow = [cashFlowBeforeDebtService[0] - PURCHASE_PRICE]
    if yearExit is not None and yearExit <= len(cashFlowBeforeDebtService):
        cashFlow += cashFlowBeforeDebtService[1: yearExit]
        if (yearExit >= len(netOperatingIncome)):
            cashFlow.append(netOperatingIncome[-1]/capRate)
        else:
            cashFlow.append(netOperatingIncome[yearExit]/capRate)
    else:
        cashFlow += cashFlowBeforeDebtService[1:]
    return cashFlow

"""
    function: getCashFlowUnleveraged
    ======================================
    Compute cash flow for unleveraged case. This function requires three input variables and one optional.

    cashFlowBeforeDebtService = cash flow before the debt of service (must be concat with empty period and match with the transation date in IRR computation)
    netOperatingIncome = net operating income (same as above)
    capRate = capital rate of the renter at the time that we exit
    yearExit = The beginning of the year that sells the building (Not recommended leave it none)
"""
def getCashFlowFutureUnleveraged(cashFlowBeforeDebtService, netOperatingIncome, capRate, yearExit=None):
    cashFlow = [cashFlowBeforeDebtService[0]]
    if yearExit is not None and yearExit <= len(cashFlowBeforeDebtService):
        cashFlow += cashFlowBeforeDebtService[1: yearExit]
        if (yearExit >= len(netOperatingIncome)):
            cashFlow.append(netOperatingIncome[-1]/capRate)
        else:
            cashFlow.append(netOperatingIncome[yearExit]/capRate)
    else:
        cashFlow += cashFlowBeforeDebtService[1:]
    return cashFlow

"""
    function: getNetCashFlowLenderA
    ===============================
    Compute net cash flow for Lender A option. This function requires one input variable yearExit.

    cashFlowBeforeDebtService = cash flow before the debt of service (must be concat with empty period and match with the transation date in IRR computation)
    netOperatingIncome = net operating income (same as above)
    yearExit = The beginning of the year that sells the building.

    The outputs of this function are

    Netcashflow = the net cash flow
    DCSR = net operating income / debt service
"""
def getNetCashFlowLenderA(totalYear, cashFlowBeforeDebtService, netOperatingIncome, yearExit=None):
    if yearExit is None: yearExit = totalYear - 1
    totalProceed = (DEPOSIT + PURCHASE_PRICE)*LENDER_A_LTV
    normalAnnualPayment = pmt(LENDER_A_INTEREST_RATE/12.0, LENDER_A_AMORTIZATION, totalProceed)*12 # Negative Value
    filled = min(yearExit, 4)
    debtService = [normalAnnualPayment for _ in xrange(filled)] + [0 for _ in xrange(filled + 1, yearExit+1)] + [0]
    fees = [LENDER_A_ENTRY_FEE*totalProceed] + [0 for _ in xrange(1, yearExit+1)]
    if (yearExit == 1):
        fees[1] = LENDER_A_EXIT_FEE*totalProceed
    if (yearExit == 2):
        fees[2] = LENDER_A_EXIT_FEE*totalProceed
    if (yearExit == 3):
        fees[2] = LENDER_A_PER_EXTENSION_FEE*totalProceed
        fees[3] = LENDER_A_EXIT_FEE*totalProceed
    if (yearExit >= 4):
        fees[2] = LENDER_A_PER_EXTENSION_FEE*totalProceed
        fees[3] = LENDER_A_PER_EXTENSION_FEE*totalProceed
        fees[4] = LENDER_A_EXIT_FEE*totalProceed
    cashflow = [(cashFlowBeforeDebtService[i] if i < len(cashFlowBeforeDebtService) else 0) + (debtService[i] if i < yearExit else 0) - fees[i] for i in xrange(yearExit + 1)]
    if yearExit < len(cashFlowBeforeDebtService): cashflow[yearExit] -= cashFlowBeforeDebtService[yearExit]

    DCSR = [-(netOperatingIncome[i] if i < len(netOperatingIncome) else 0)/debtService[i] for i in xrange(min(yearExit, 4))]
    return cashflow, DCSR

"""
    function: getLeveragedCashFlowLenderA
    =====================================
    Compute the leveraged cash flow for Lender A option.
    This function requires the input from getNashCashFlowLenderA function.

    netOperatingIncome = net operating income (must be concat with empty period and match with the transation date in IRR computation)
    capRate = capital rate of the renter at the time that we exit
"""
def getLeveragedCashFlowLenderA(netCashFlow, netOperatingIncome, capRate, yearExit, isEnd=True):
    loanTakeOut = (DEPOSIT + PURCHASE_PRICE)*LENDER_A_LTV
    if (len(netCashFlow) > len(netOperatingIncome)):
        salePriceWithCapRate = netOperatingIncome[-1]/capRate
    else:
        salePriceWithCapRate = netOperatingIncome[len(netCashFlow)-1]/capRate
    leveragedCashFlow = [netCashFlow[0] - PURCHASE_PRICE + loanTakeOut] + netCashFlow[1:]
    mortgageExpireYear = min(4, yearExit)
    totalProceed = (DEPOSIT + PURCHASE_PRICE)*LENDER_A_LTV
    normalAnnualPayment = pmt(LENDER_A_INTEREST_RATE/12.0, LENDER_A_AMORTIZATION, totalProceed)*12 # Negative Value
    # leveragedCashFlow[mortgageExpireYear] -= pv(LENDER_A_INTEREST_RATE/12.0, LENDER_A_AMORTIZATION - 12*mortgageExpireYear, normalAnnualPayment/12)
    if isEnd: leveragedCashFlow[-1] += salePriceWithCapRate
    return leveragedCashFlow

"""
    function: getNetCashFlowLenderB
    ===============================
    Compute net cash flow for Lender B option. This function requires one input variable yearExit.

    yearExit = The beginning of the year that sells the building.

    The outputs of this function are

    Netcashflow = the net cash flow
    DCSR = net operating income / debt service
"""
def getNetCashFlowLenderB(totalYear, cashFlowBeforeDebtService, netOperatingIncome, yearExit=None):
    if yearExit is None: yearExit = totalYear
    if yearExit < 4: raise Exception("yearExit must be at least 4")
    totalProceed = (DEPOSIT + PURCHASE_PRICE)*LENDER_B_LTV
    interestOnlyPayment = -LENDER_B_INTEREST_RATE*totalProceed # Negative Value
    normalAnnualPayment = pmt(LENDER_B_INTEREST_RATE/12.0, LENDER_B_AMORTIZATION, totalProceed)*12 # Negative Value
    debtService = [interestOnlyPayment, interestOnlyPayment] + [normalAnnualPayment for _ in xrange(2, min(5, yearExit))] + [0 for _ in xrange(min(5, yearExit), yearExit)] #Negative Value
    entryFee = LENDER_B_ENTRY_FEE*totalProceed
    netCashFlow = [(cashFlowBeforeDebtService[i] if i < len(cashFlowBeforeDebtService) else 0) + debtService[i] for i in xrange(yearExit)] + [0]
    netCashFlow[0] -= entryFee
    if yearExit == 4:
        totalProceed = (DEPOSIT + PURCHASE_PRICE)*LENDER_B_LTV
        normalAnnualPayment = pmt(LENDER_B_INTEREST_RATE/12.0, LENDER_B_AMORTIZATION, totalProceed)*12 # Negative Value
        mortgageExpireYear = 4
        mortgageBalance = pv(LENDER_B_INTEREST_RATE/12.0, LENDER_B_AMORTIZATION - 12*(mortgageExpireYear-2), normalAnnualPayment/12)
        netCashFlow[4] = (LENDER_B_INTEREST_RATE - TREASURY_YIELD)*((1 - (1 + TREASURY_YIELD))/TREASURY_YIELD)*mortgageBalance
    DCSR = [-(netOperatingIncome[i] if i < len(netOperatingIncome) else 0)/debtService[i] for i in xrange(min(yearExit, 5))]
    return netCashFlow, DCSR

"""
    function: getLeveragedCashFlowLenderB
    =====================================
    Compute the leveraged cash flow for Lender B option.
    This function requires the input from getNashCashFlowLenderB function.

    netOperatingIncome = net operating income (must be concat with empty period and match with the transation date in IRR computation)
    capRate = capital rate of the renter at the time that we exit
"""
def getLeveragedCashFlowLenderB(netCashFlow, netOperatingIncome, capRate, yearExit, isEnd=True):
    loanTakeOut = (DEPOSIT + PURCHASE_PRICE)*LENDER_B_LTV
    if (len(netCashFlow) > len(netOperatingIncome)):
        salePriceWithCapRate = netOperatingIncome[-1]/capRate
    else:
        salePriceWithCapRate = netOperatingIncome[len(netCashFlow)-1]/capRate
    leveragedCashFlow = [netCashFlow[0] - PURCHASE_PRICE + loanTakeOut] + netCashFlow[1:]
    mortgageExpireYear = min(5, yearExit)
    totalProceed = (DEPOSIT + PURCHASE_PRICE)*LENDER_B_LTV
    normalAnnualPayment = pmt(LENDER_B_INTEREST_RATE/12.0, LENDER_B_AMORTIZATION, totalProceed)*12 # Negative Value
    leveragedCashFlow[mortgageExpireYear] -= pv(LENDER_B_INTEREST_RATE/12.0, LENDER_B_AMORTIZATION - 12*(mortgageExpireYear-2), normalAnnualPayment/12)
    if isEnd: leveragedCashFlow[-1] += salePriceWithCapRate
    return leveragedCashFlow

"""
    function: computeIRRWithNoSunkCost
    ==================================
    Compute IRR with no sunk cost. This function requires two input variables: cashFlow and transaction_date.

    cashFlow = [cashflow1, cashflow2, ...]
    transaction_date = [date 1 of the cash flow, date 2 of the cash flow, ...]
"""
def computeIRRWithNoSunkCost(cashFlow, transaction_date=None):
    if transaction_date is None:
        transaction_date = [date(i, 7, 1) for i in xrange(2015, 2015 + len(cashFlow))]
    cashFlowData = map(lambda x, y: (x,y), transaction_date, cashFlow)
    return xirr(cashFlowData)

"""
    function: computeIRR
    ====================
    Compute IRR with sunk cost. This function requires two input variables: cashFlow and transaction_date.

    cashFlow = [cashflow1, cashflow2, ...]
    transaction_date = [date 1 of the cash flow, date 2 of the cash flow, ...]
"""
def computeIRR(cashFlow, transaction_date=None):
    if transaction_date is None:
        transaction_date = [date(i, 7, 1) for i in xrange(2015, 2015 + len(cashFlow))]
    transaction_date = [date(2013, 4, 1), date(2014, 7, 1)] + transaction_date
    cashFlowData = map(lambda x, y: (x,y), transaction_date, [-DEPOSIT, 0] + cashFlow)
    return xirr(cashFlowData)

"""
    function: computeEquityMultipleWithNoSunkCost
    =============================================
    Compute equity multiple with no sunk cost. This function requires cashFlow
"""
def computeEquityMultipleWithNoSunkCost(cashFlow):
    nom, denom = 0, 0
    for cf in cashFlow:
        if cf > 0: nom += cf
        else: denom -= cf
    return float(nom)/denom

"""
    function: computeEquityMultipleWithNoSunkCost
    =============================================
    Compute equity multiple. This function requires cashFlow
"""
def computeEquityMultiple(cashFlow):
    nom, denom = 0, DEPOSIT
    for cf in cashFlow:
        if cf > 0: nom += cf
        else: denom -= cf
    return float(nom)/denom


topshop =   Renter(
                name = 'TopShop',
                initialRentPerSqm = 833,
                term = 10,
                annualIncrease = 0.025,
                isGuarantee = False,
                abatement = 0,
                ti = 200,
                capRate = 0.08
            )

zara    =   Renter(
                name = 'Zara',
                initialRentPerSqm = 583,
                term = 12,
                annualIncrease = 0.025,
                isGuarantee = True,
                abatement = 12,
                ti = 600,
                capRate = 0.055
            )

decathlon = Renter(
                name = 'Decathlon',
                initialRentPerSqm = 708,
                term = 10,
                annualIncrease = 0.025,
                isGuarantee = True,
                abatement = 9,
                ti = 400,
                capRate = 0.055
            )

# print getCashFlowUnleveraged(cashFlowBeforeDebtService=topshop.getCashFlowBeforeDebtService(),
#                         netOperatingIncome=topshop.getNetOperatingIncome(),
#                         capRate=topshop.getCapRate(), yearExit=6)
# #
# netCashFlowA, DCSR = getNetCashFlowLenderA(yearExit=1,
#                                            totalYear=topshop.getTerm(),
#                                            cashFlowBeforeDebtService=topshop.getCashFlowBeforeDebtService(),
#                                            netOperatingIncome=topshop.getNetOperatingIncome())
#
# getLeveragedCashFlowLenderA(netCashFlowA, topshop.getNetOperatingIncome(), topshop.getCapRate())
#
# netCashFlowB, DCSR = getNetCashFlowLenderB(yearExit=5,
#                                            totalYear=topshop.getTerm(),
#                                            cashFlowBeforeDebtService=topshop.getCashFlowBeforeDebtService(),
#                                            netOperatingIncome=topshop.getNetOperatingIncome())
#
# getLeveragedCashFlowLenderB(netCashFlowB, topshop.getNetOperatingIncome(), topshop.getCapRate())
