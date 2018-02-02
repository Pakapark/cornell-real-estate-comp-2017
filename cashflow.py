from scipy.stats import poisson
from datetime import date
from copy import deepcopy
from math import ceil
from numpy import pv
import renter

# Assumption on future tenant
INITIAL_RENT_PER_SQM_AT_2015 = 708
ANNUAL_INCREASE = 0.025
IS_GUARANTEE = True
ABATEMENT = 9
TI = 400
CAP_RATE = 0.055
FUTURE_TERM = 10

# Poisson Assumption on Empty Space
POISSON_EMPTY_MEAN = 4
POISSON_EMPTY_LOWER_TRUNCATE = 2
POISSON_EMPTY_UPPER_TRUNCATE = 8

def truncated_poisson():
    poisson_dist = poisson(POISSON_EMPTY_MEAN)
    probs = [poisson_dist.pmf(i) for i in xrange(POISSON_EMPTY_UPPER_TRUNCATE)]
    return {0: sum(probs[0:3]), 1: probs[3], 2: probs[4], 3: probs[5], 4: probs[6], 5: probs[7], 6: 1 - sum(probs)}

POISSON_EMPTY_DIST = truncated_poisson()

topshop = renter.topshop
zara = renter.zara
decathlon = renter.decathlon

'''
    function: topshopOutcome
    ========================
    Compute IRR and Equity Multiple given the year that Topshop and
    the year that the building is sold
'''
def topshopUnleveragedOutcome(renter_exit_year, sell_year, capRate):
    topshop.setTerm(renter_exit_year)
    topshop.setCapRate(capRate)

    if sell_year <= renter_exit_year:
        topshopCashFlow = renter.getCashFlowUnleveraged(cashFlowBeforeDebtService=topshop.getCashFlowBeforeDebtService(),
                                                        netOperatingIncome=topshop.getNetOperatingIncome(),
                                                        capRate=topshop.getCapRate(), yearExit=sell_year)

        irr = renter.computeIRR(topshopCashFlow)
        irrWithNoSunkCost = renter.computeIRRWithNoSunkCost(topshopCashFlow)
        equityMultiple = renter.computeEquityMultiple(topshopCashFlow)
        equityMultipleWithNoSunkCost = renter.computeEquityMultipleWithNoSunkCost(topshopCashFlow)
    else:
        topshopCashFlow = renter.getCashFlowUnleveraged(cashFlowBeforeDebtService=topshop.getCashFlowBeforeDebtService(),
                                                        netOperatingIncome=topshop.getNetOperatingIncome(),
                                                        capRate=topshop.getCapRate())

        topshop_transaction_date = [date(i, 7, 1) for i in xrange(2015, 2015 + renter_exit_year)]

        irr = 0
        irrWithNoSunkCost = 0
        equityMultiple = 0
        equityMultipleWithNoSunkCost = 0

        for q in POISSON_EMPTY_DIST:
            prob = POISSON_EMPTY_DIST[q]
            topshopCashFlowCopy = deepcopy(topshopCashFlow)
            maintentanceCost = 3*q/12.0*topshop.getOperatingExpense()[-1]*topshop.getAnnualIncrease()
            topshopCashFlowCopy.append(maintentanceCost)
            nextTransactionYear = 2015 + renter_exit_year + (3*q + 7)/12
            nextTransactionMonth = (7 + 3*q) % 12
            futureTerm = max(1, sell_year - renter_exit_year - int(ceil(3*q/12)))
            transaction_date = [date(nextTransactionYear + i, nextTransactionMonth, 1) for i in xrange(futureTerm + 1)]

            randomRenter = renter.Renter('unknown',
                                         INITIAL_RENT_PER_SQM_AT_2015 * (1 + ANNUAL_INCREASE)**(renter_exit_year + 3*q/12.0) ,
                                         FUTURE_TERM, ANNUAL_INCREASE, IS_GUARANTEE, ABATEMENT, TI, CAP_RATE)

            randomCashFlow = renter.getCashFlowFutureUnleveraged(cashFlowBeforeDebtService=randomRenter.getCashFlowBeforeDebtService(),
                                                               netOperatingIncome=randomRenter.getNetOperatingIncome(),
                                                               capRate=randomRenter.getCapRate(),
                                                               yearExit=futureTerm)


            if q == 0:
                topshopCashFlowCopy[-1] += randomCashFlow[0]
                mergeCashFlow = topshopCashFlowCopy + randomCashFlow[1:]
                mergeTransactionDate = topshop_transaction_date + transaction_date
                randomRenterIRR = renter.computeIRR(mergeCashFlow, mergeTransactionDate)
                randomRenterIRRWithNoSunkCost = renter.computeIRRWithNoSunkCost(mergeCashFlow, mergeTransactionDate)
            else:
                mergeCashFlow = topshopCashFlowCopy + randomCashFlow
                mergeTransactionDate = topshop_transaction_date + [date(2015 + renter_exit_year, 7, 1)] + transaction_date
                randomRenterIRR = renter.computeIRR(mergeCashFlow, mergeTransactionDate)
                randomRenterIRRWithNoSunkCost = renter.computeIRRWithNoSunkCost(mergeCashFlow, mergeTransactionDate)


            irr += prob * randomRenterIRR
            irrWithNoSunkCost += prob * randomRenterIRRWithNoSunkCost
            equityMultiple += prob * renter.computeEquityMultiple(mergeCashFlow)
            equityMultipleWithNoSunkCost += prob * renter.computeEquityMultipleWithNoSunkCost(mergeCashFlow)

    return irr, irrWithNoSunkCost, equityMultiple, equityMultipleWithNoSunkCost

"""
    function: topshopLenderAOutcome
    ===============================
    Compute the IRR and equity multiple for Topshop in case of lending option A
"""
def topshopLenderAOutcome(renter_exit_year, sell_year, capRate):
    topshop.setTerm(renter_exit_year)
    topshop.setCapRate(capRate)

    if sell_year <= renter_exit_year:
        topshopCashFlow, DCSR = renter.getNetCashFlowLenderA(topshop.getTerm(), topshop.getCashFlowBeforeDebtService(), topshop.getNetOperatingIncome(), yearExit=sell_year)
        topshopCashFlow = renter.getLeveragedCashFlowLenderA(topshopCashFlow, topshop.getNetOperatingIncome(), topshop.getCapRate(), yearExit=sell_year)

        print topshopCashFlow

        irr = renter.computeIRR(topshopCashFlow)
        irrWithNoSunkCost = renter.computeIRRWithNoSunkCost(topshopCashFlow)
        equityMultiple = renter.computeEquityMultiple(topshopCashFlow)
        equityMultipleWithNoSunkCost = renter.computeEquityMultipleWithNoSunkCost(topshopCashFlow)
    else:
        topshopCashFlow, DCSR = renter.getNetCashFlowLenderA(topshop.getTerm(), topshop.getCashFlowBeforeDebtService(), topshop.getNetOperatingIncome(), yearExit=sell_year)

        topshopCashFlow = renter.getLeveragedCashFlowLenderA(topshopCashFlow, topshop.getNetOperatingIncome(), topshop.getCapRate(), yearExit=sell_year, isEnd=False)
        topshop_transaction_date = [date(i, 7, 1) for i in xrange(2015, 2015 + len(topshopCashFlow) + 1)]

        irr = 0
        irrWithNoSunkCost = 0
        equityMultiple = 0
        equityMultipleWithNoSunkCost = 0

        q = 0
        prob = 1
        topshopCashFlowCopy = deepcopy(topshopCashFlow)
        maintentanceCost = 3*q/12.0*topshop.getOperatingExpense()[-1]*topshop.getAnnualIncrease()
        topshopCashFlowCopy.append(maintentanceCost)
        nextTransactionYear = 2015 + renter_exit_year + (3*q + 7)/12
        nextTransactionMonth = (7 + 3*q) % 12
        futureTerm = max(1, sell_year - renter_exit_year - int(ceil(3*q/12)))
        transaction_date = [date(nextTransactionYear + i, nextTransactionMonth, 1) for i in xrange(futureTerm + 1)]

        randomRenter = renter.Renter('unknown',
                                     INITIAL_RENT_PER_SQM_AT_2015 * (1 + ANNUAL_INCREASE)**(renter_exit_year + 3*q/12.0) ,
                                     FUTURE_TERM, ANNUAL_INCREASE, IS_GUARANTEE, ABATEMENT, TI, CAP_RATE)

        randomCashFlow = renter.getCashFlowFutureUnleveraged(cashFlowBeforeDebtService=randomRenter.getCashFlowBeforeDebtService(),
                                                           netOperatingIncome=randomRenter.getNetOperatingIncome(),
                                                           capRate=randomRenter.getCapRate(),
                                                           yearExit=futureTerm)

        mergeCashFlow = topshopCashFlowCopy + randomCashFlow
        mergeCashFlow[-1] -= -pv(0.05/12.0, 240 - 12*sell_year, 1108726/12.0)
        print mergeCashFlow

        # print "mortgage: " + repr(-pv(0.05/12.0, 240 - 12*sell_year, 1108726/12.0))
        # print mergeCashFlow
        mergeTransactionDate = topshop_transaction_date + transaction_date
        print mergeTransactionDate
        randomRenterIRR = renter.computeIRR(mergeCashFlow, mergeTransactionDate)
        randomRenterIRRWithNoSunkCost = renter.computeIRRWithNoSunkCost(mergeCashFlow, mergeTransactionDate)

        irr += prob * randomRenterIRR
        irrWithNoSunkCost += prob * randomRenterIRRWithNoSunkCost
        equityMultiple += prob * renter.computeEquityMultiple(mergeCashFlow)
        equityMultipleWithNoSunkCost += prob * renter.computeEquityMultipleWithNoSunkCost(mergeCashFlow)

    return irr, irrWithNoSunkCost, equityMultiple, equityMultipleWithNoSunkCost


"""
    function: topshopLenderBOutcome
    ===============================
    Compute the IRR and equity multiple for Topshop in case of lending option B
"""
def topshopLenderBOutcome(renter_exit_year, sell_year, capRate):
    topshop.setTerm(renter_exit_year)
    topshop.setCapRate(capRate)

    if sell_year <= renter_exit_year:
        topshopCashFlow, DCSR = renter.getNetCashFlowLenderB(topshop.getTerm(), topshop.getCashFlowBeforeDebtService(), topshop.getNetOperatingIncome(), yearExit=sell_year)
        topshopCashFlow = renter.getLeveragedCashFlowLenderB(topshopCashFlow, topshop.getNetOperatingIncome(), topshop.getCapRate(), yearExit=sell_year)

        irr = renter.computeIRR(topshopCashFlow)
        irrWithNoSunkCost = renter.computeIRRWithNoSunkCost(topshopCashFlow)
        equityMultiple = renter.computeEquityMultiple(topshopCashFlow)
        equityMultipleWithNoSunkCost = renter.computeEquityMultipleWithNoSunkCost(topshopCashFlow)
    else:
        topshopCashFlow, DCSR = renter.getNetCashFlowLenderA(topshop.getTerm(), topshop.getCashFlowBeforeDebtService(), topshop.getNetOperatingIncome(), yearExit=sell_year)
        topshopCashFlow = renter.getLeveragedCashFlowLenderA(topshopCashFlow, topshop.getNetOperatingIncome(), topshop.getCapRate(), yearExit=sell_year, isEnd=False)
        topshop_transaction_date = [date(i, 7, 1) for i in xrange(2015, 2015 + len(topshopCashFlow) + 1)]

        irr = 0
        irrWithNoSunkCost = 0
        equityMultiple = 0
        equityMultipleWithNoSunkCost = 0

        for q in POISSON_EMPTY_DIST:
            prob = POISSON_EMPTY_DIST[q]
            topshopCashFlowCopy = deepcopy(topshopCashFlow)
            maintentanceCost = 3*q/12.0*topshop.getOperatingExpense()[-1]*topshop.getAnnualIncrease()
            topshopCashFlowCopy.append(maintentanceCost)
            nextTransactionYear = 2015 + renter_exit_year + (3*q + 7)/12
            nextTransactionMonth = (7 + 3*q) % 12
            futureTerm = max(1, sell_year - renter_exit_year - int(ceil(3*q/12)))
            transaction_date = [date(nextTransactionYear + i, nextTransactionMonth, 1) for i in xrange(futureTerm + 1)]

            randomRenter = renter.Renter('unknown',
                                         INITIAL_RENT_PER_SQM_AT_2015 * (1 + ANNUAL_INCREASE)**(renter_exit_year + 3*q/12.0) ,
                                         FUTURE_TERM, ANNUAL_INCREASE, IS_GUARANTEE, ABATEMENT, TI, CAP_RATE)

            randomCashFlow = renter.getCashFlowFutureUnleveraged(cashFlowBeforeDebtService=randomRenter.getCashFlowBeforeDebtService(),
                                                               netOperatingIncome=randomRenter.getNetOperatingIncome(),
                                                               capRate=randomRenter.getCapRate(),
                                                               yearExit=futureTerm)

            mergeCashFlow = topshopCashFlowCopy + randomCashFlow
            mergeTransactionDate = topshop_transaction_date + transaction_date
            randomRenterIRR = renter.computeIRR(mergeCashFlow, mergeTransactionDate)
            randomRenterIRRWithNoSunkCost = renter.computeIRRWithNoSunkCost(mergeCashFlow, mergeTransactionDate)

            irr += prob * randomRenterIRR
            irrWithNoSunkCost += prob * randomRenterIRRWithNoSunkCost
            equityMultiple += prob * renter.computeEquityMultiple(mergeCashFlow)
            equityMultipleWithNoSunkCost += prob * renter.computeEquityMultipleWithNoSunkCost(mergeCashFlow)

    return irr, irrWithNoSunkCost, equityMultiple, equityMultipleWithNoSunkCost

def zaraUnleveragedOutcome(sell_year, capRate):
    zara.setCapRate(capRate)
    zaraCashFlow = renter.getCashFlowUnleveraged(cashFlowBeforeDebtService=zara.getCashFlowBeforeDebtService(),
                                                    netOperatingIncome=zara.getNetOperatingIncome(),
                                                    capRate=zara.getCapRate(), yearExit=sell_year)

    irr = renter.computeIRR(zaraCashFlow)
    irrWithNoSunkCost = renter.computeIRRWithNoSunkCost(zaraCashFlow)
    equityMultiple = renter.computeEquityMultiple(zaraCashFlow)
    equityMultipleWithNoSunkCost = renter.computeEquityMultipleWithNoSunkCost(zaraCashFlow)
    return irr, irrWithNoSunkCost, equityMultiple, equityMultipleWithNoSunkCost

def zaraLenderAOutcome(sell_year, capRate):
    zara.setCapRate(capRate)
    zaraCashFlow, DSCR = renter.getNetCashFlowLenderA(zara.getTerm(), zara.getCashFlowBeforeDebtService(), zara.getNetOperatingIncome(), yearExit=sell_year)
    zaraCashFlow = renter.getLeveragedCashFlowLenderA(zaraCashFlow, zara.getNetOperatingIncome(), zara.getCapRate(), yearExit=sell_year)

    irr = renter.computeIRR(zaraCashFlow)
    irrWithNoSunkCost = renter.computeIRRWithNoSunkCost(zaraCashFlow)
    equityMultiple = renter.computeEquityMultiple(zaraCashFlow)
    equityMultipleWithNoSunkCost = renter.computeEquityMultipleWithNoSunkCost(zaraCashFlow)
    return irr, irrWithNoSunkCost, equityMultiple, equityMultipleWithNoSunkCost

def zaraLenderBOutcome(sell_year, capRate):
    zara.setCapRate(capRate)
    zaraCashFlow, DCSR = renter.getNetCashFlowLenderB(zara.getTerm(), zara.getCashFlowBeforeDebtService(), zara.getNetOperatingIncome(), yearExit=sell_year)
    zaraCashFlow = renter.getLeveragedCashFlowLenderB(zaraCashFlow, zara.getNetOperatingIncome(), zara.getCapRate(), yearExit=sell_year)

    irr = renter.computeIRR(zaraCashFlow)
    irrWithNoSunkCost = renter.computeIRRWithNoSunkCost(zaraCashFlow)
    equityMultiple = renter.computeEquityMultiple(zaraCashFlow)
    equityMultipleWithNoSunkCost = renter.computeEquityMultipleWithNoSunkCost(zaraCashFlow)
    return irr, irrWithNoSunkCost, equityMultiple, equityMultipleWithNoSunkCost

def decathlonUnleveragedOutcome(sell_year, capRate):
    decathlon.setCapRate(capRate)
    decathlonCashFlow = renter.getCashFlowUnleveraged(cashFlowBeforeDebtService=decathlon.getCashFlowBeforeDebtService(),
                                                    netOperatingIncome=decathlon.getNetOperatingIncome(),
                                                    capRate=decathlon.getCapRate(), yearExit=sell_year)

    irr = renter.computeIRR(decathlonCashFlow)
    irrWithNoSunkCost = renter.computeIRRWithNoSunkCost(decathlonCashFlow)
    equityMultiple = renter.computeEquityMultiple(decathlonCashFlow)
    equityMultipleWithNoSunkCost = renter.computeEquityMultipleWithNoSunkCost(decathlonCashFlow)
    return irr, irrWithNoSunkCost, equityMultiple, equityMultipleWithNoSunkCost

def decathlonLenderAOutcome(sell_year, capRate):
    decathlon.setCapRate(capRate)

    decathlonCashFlow, DSCR = renter.getNetCashFlowLenderA(decathlon.getTerm(), decathlon.getCashFlowBeforeDebtService(), decathlon.getNetOperatingIncome(), yearExit=sell_year)
    decathlonCashFlow = renter.getLeveragedCashFlowLenderA(decathlonCashFlow, decathlon.getNetOperatingIncome(), decathlon.getCapRate(), yearExit=sell_year)

    print decathlonCashFlow

    irr = renter.computeIRR(decathlonCashFlow)
    irrWithNoSunkCost = renter.computeIRRWithNoSunkCost(decathlonCashFlow)
    equityMultiple = renter.computeEquityMultiple(decathlonCashFlow)
    equityMultipleWithNoSunkCost = renter.computeEquityMultipleWithNoSunkCost(decathlonCashFlow)
    return irr, irrWithNoSunkCost, equityMultiple, equityMultipleWithNoSunkCost

def decathlonLenderBOutcome(sell_year, capRate):
    decathlon.setCapRate(capRate)
    decathlonCashFlow, DCSR = renter.getNetCashFlowLenderB(decathlon.getTerm(), decathlon.getCashFlowBeforeDebtService(), decathlon.getNetOperatingIncome(), yearExit=sell_year)
    decathlonCashFlow = renter.getLeveragedCashFlowLenderB(decathlonCashFlow, decathlon.getNetOperatingIncome(), decathlon.getCapRate(), yearExit=sell_year)

    irr = renter.computeIRR(decathlonCashFlow)
    irrWithNoSunkCost = renter.computeIRRWithNoSunkCost(decathlonCashFlow)
    equityMultiple = renter.computeEquityMultiple(decathlonCashFlow)
    equityMultipleWithNoSunkCost = renter.computeEquityMultipleWithNoSunkCost(decathlonCashFlow)
    return irr, irrWithNoSunkCost, equityMultiple, equityMultipleWithNoSunkCost
