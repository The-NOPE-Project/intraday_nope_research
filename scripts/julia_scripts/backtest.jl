using Dates
using Statistics

include("./inputData.jl")

function backtestShortNope()
    #gets the data as dicts where timestamp points to data
    (timestampToNope, timestampToPrice, orderedDates, dateFormat) = getData()

    day = Dates.day(DateTime(orderedDates[1],dateFormat))

    dayStartTime = Time("09:30")
    dayEndTime = Time("16:00")
    marketClose = Time("16:00")
    datasetOfInterest = Any[]#entry, exit, stopLoss, successrate, PNL

    println("Beginning Analysis")
    for i in 0:5:90
        println("updated i ", "$i")
        for j in i+10:5:95
            #println("updated j ", "$i $j")
            #for k in j+10:10:150
                shortEntry = j
                shortExit = i
                stopLoss = 100

                stopDay = nothing

                values = Any[]
                holdTimes = Float64[]
                entryTime = nothing
                returns = Float64[]
                tradeInProgress = false
                entryPrice = nothing
                exitPrice = nothing
                totalPNL = 0
                successes = 0
                fails = 0
                for dateIndex in 1:length(orderedDates)
                    date = orderedDates[dateIndex]
                    finalTimeOfDay = false
                    if dateIndex<length(orderedDates)
                        nextDate = orderedDates[dateIndex+1]
                        currentDay = Dates.day(DateTime(date,dateFormat))
                        nextDay = Dates.day(DateTime(nextDate,dateFormat))
                        if currentDay != nextDay
                            finalTimeOfDay = true
                        end
                    end
                    datetime = DateTime(date, dateFormat)
                    time = Time(datetime)
                    nope = timestampToNope[date]*100
                    price = timestampToPrice[date]

                    if nope >= shortEntry && !tradeInProgress && time >= dayStartTime && time <= dayEndTime && nope<stopLoss
                        entryPrice = [nope, date, price]
                        tradeInProgress = true
                        entryTime = time
                    end
                    if tradeInProgress && ((nope<=shortExit || nope>=stopLoss) || time >= marketClose || finalTimeOfDay)
                        exitPrice = [nope,date, price]
                        push!(values,entryPrice, exitPrice)
                        pnl = entryPrice[3] - exitPrice[3]
                        entryMinutes = minute(entryTime) + (hour(entryTime)*60)
                        exitMinutes = minute(time) + (hour(time)*60)
                        push!(holdTimes, exitMinutes - entryMinutes)
                        entryTime = nothing
                        push!(returns, pnl)
                        if pnl < 0
                            fails = fails + 1
                        else
                            successes = successes + 1
                        end
                        totalPNL = totalPNL + pnl
                        tradeInProgress = false
                        entryPrice = nothing
                        exitPrice = nothing
                    end
                end
                push!(datasetOfInterest, [shortEntry, shortExit, stopLoss,successes/(successes+fails),successes+fails,totalPNL, Statistics.mean(returns), Statistics.std(returns), Statistics.mean(holdTimes),Statistics.median(holdTimes)])
            #end
        end
    end
    writeResults(datasetOfInterest)
end

function backtestLongNope()
    #gets the data as dicts where timestamp points to data
    (timestampToNope, timestampToPrice, orderedDates, dateFormat) = getData()

    day = Dates.day(DateTime(orderedDates[1],dateFormat))

    dayStartTime = Time("09:30")
    dayEndTime = Time("16:00")
    marketClose = Time("16:00")
    datasetOfInterest = Any[]#entry, exit, stopLoss, successrate, PNL

    println("Beginning Analysis")
    for i in -120:5:-10
        println("updated i ", "$i")
        for j in i+10:5:0
            #println("updated j ", "$i $j")
            #for k in j+10:10:150
                longEntry = i
                longExit = j
                stopLoss = -1000

                values = Any[]
                holdTimes = Float64[]
                entryTime = nothing
                returns = Float64[]
                tradeInProgress = false
                entryPrice = nothing
                exitPrice = nothing
                totalPNL = 0
                successes = 0
                fails = 0
                for dateIndex in 1:length(orderedDates)
                    date = orderedDates[dateIndex]
                    finalTimeOfDay = false
                    if dateIndex<length(orderedDates)
                        nextDate = orderedDates[dateIndex+1]
                        currentDay = Dates.day(DateTime(date,dateFormat))
                        nextDay = Dates.day(DateTime(nextDate,dateFormat))
                        if currentDay != nextDay
                            finalTimeOfDay = true
                        end
                    end
                    datetime = DateTime(date, dateFormat)
                    time = Time(datetime)
                    nope = timestampToNope[date]*100
                    price = timestampToPrice[date]

                    if nope <= longEntry && !tradeInProgress && time >= dayStartTime && time < dayEndTime && nope>stopLoss
                        entryPrice = [nope, date, price]
                        tradeInProgress = true
                        entryTime = time
                    end
                    if tradeInProgress && ((nope>longExit || nope<stopLoss) || time >= marketClose || finalTimeOfDay)
                        exitPrice = [nope,date, price]
                        push!(values,entryPrice, exitPrice)
                        pnl = exitPrice[3] - entryPrice[3]
                        entryMinutes = minute(entryTime) + (hour(entryTime)*60)
                        exitMinutes = minute(time) + (hour(time)*60)
                        push!(holdTimes, exitMinutes - entryMinutes)
                        entryTime = nothing
                        push!(returns, pnl)
                        if pnl < 0
                            fails = fails + 1
                        else
                            successes = successes + 1
                        end
                        totalPNL = totalPNL + pnl
                        tradeInProgress = false
                        entryPrice = nothing
                        exitPrice = nothing
                    end
                end
                push!(datasetOfInterest, [longEntry, longExit, stopLoss,successes/(successes+fails),successes+fails,totalPNL, Statistics.mean(returns), Statistics.std(returns), Statistics.mean(holdTimes),Statistics.median(holdTimes)])
            #end
        end
    end
    writeResults(datasetOfInterest)
end

function writeResults(dataSet::Array{Any},fileName::String= "results",folderPath::String = "./")
    file = open(string(folderPath,fileName,".csv"),"w")
        write(file,string("entry_nope,exit_nope,stop_loss_nope,success_rate,total_trades,total_PNL,mean_of_returns,standard_deviation,average_hold_time,median_hold_time", "\n"))
        for row in dataSet
            write(file,string(row[1],",",row[2],",",row[3],",",row[4],",",row[5],",", row[6],",", row[7],",", row[8],",", row[9], ",",row[10],"\n"))
        end
    close(file)
end
