using Dates
using Statistics

include("./inputData.jl")

function mergedBacktest(shortEntry = 30, shortExit = 15, longEntry = -60, longExit = -40)
    #gets the data as dicts where timestamp points to data
    (timestampToNope, timestampToPrice, orderedDates, dateFormat) = getData()

    day = Dates.day(DateTime(orderedDates[1],dateFormat))

    dayStartTime = Time("09:30")
    dayEndTime = Time("16:00")
    marketClose = Time("16:00")
    datasetOfInterest = Any[]

    println("Beginning Analysis")

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
    longTrade=false
    shortTrade=false
    lastTradeDay = 0
    #iterate over all timestamps in order
    for dateIndex in 1:length(orderedDates)
        #variable to a startegy where only one trade is made each day
        date = orderedDates[dateIndex]
        currentDay = Dates.day(DateTime(date,dateFormat))
        #finds out if a timestamp is the last in the day
        finalTimeOfDay = false
        if dateIndex<length(orderedDates)
            nextDate = orderedDates[dateIndex+1]
            nextDay = Dates.day(DateTime(nextDate,dateFormat))
            if currentDay != nextDay
                finalTimeOfDay = true
            end
        end

        datetime = DateTime(date, dateFormat)
        time = Time(datetime)
        #get nope an price
        nope = timestampToNope[date]*100
        price = timestampToPrice[date]


        #enter a trade
        if (nope <= longEntry || nope >= shortEntry) && !tradeInProgress && time >= dayStartTime && time < dayEndTime && currentDay != lastTradeDay
            entryPrice = [nope, date, price]
            tradeInProgress = true
            tradeMade = true
            entryTime = time
            if nope<=longEntry
                longTrade = true
            elseif nope>= shortEntry
                shortTrade = true
            end
            lastTradeDay = Dates.day(DateTime(date,dateFormat))
        end
        #close a trade
        if tradeInProgress && ((nope>=longExit && longTrade) || (nope<=shortExit && shortTrade) || time >= marketClose || finalTimeOfDay)
            exitPrice = [nope,date, price]

            push!(values,entryPrice, exitPrice)
            if longTrade
                pnl = exitPrice[3] - entryPrice[3]
            elseif shortTrade
                pnl = entryPrice[3] - exitPrice[3]
            end
            if longTrade
                println("Long:", round(entryPrice[1],digits=2), "=>", exitPrice[1], " , ", entryPrice[3], "=>", exitPrice[3], " , ", round(pnl, digits = 2), " , ",entryPrice[2], "=>", exitPrice[2])
            else
                println("Short:", round(entryPrice[1],digits=2), "=>", exitPrice[1], " , ", entryPrice[3], "=>", exitPrice[3], " , ", round(pnl, digits = 2), " , ",entryPrice[2], "=>", exitPrice[2])
            end
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
            longTrade = false
            shortTrade = false
        end
    end
    push!(datasetOfInterest, [shortEntry, shortExit, longEntry, longExit, successes/(successes+fails),successes+fails,totalPNL, Statistics.mean(returns), Statistics.median(returns),Statistics.mean(holdTimes),Statistics.median(holdTimes)])
    writeResults(datasetOfInterest)
end

function writeResults(dataSet::Array{Any},fileName::String= "results",folderPath::String = "./")
    file = open(string(folderPath,fileName,".csv"),"w")
        write(file,string("short_entry,short_exit, long_entry, long_exit,success_rate,total_trades,total_PNL,mean_of_returns,median_of_returns,average_hold_time,median_hold_time", "\n"))
        for row in dataSet
            write(file,string(row[1],",",row[2],",",row[3],",",row[4],",",row[5],",", row[6],",", row[7],",", row[8],",", row[9],",", row[10],",",row[11],"\n"))
        end
    close(file)
end
