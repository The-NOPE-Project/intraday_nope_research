function getData()
    println("Loading Data (very fast)")
    timestampToPrice = getPriceData()
    timestampToNope = getNopeData()

    dateFormat = "mm/dd/yyyy H:M"
    orderedDates = String[]
    for key in keys(timestampToNope)
        push!(orderedDates, key)
    end
    println("Sorting Dates (about 1 min)")
    sort!(orderedDates, by = x -> DateTime(x, "mm/dd/yyyy H:M"))
    return timestampToNope, timestampToPrice, orderedDates, dateFormat
end

function getNopeData()
    dataFiles = ["../processed_data/parsedNetDelta2020-01.csv", "../processed_data/parsedNetDelta2020-02.csv","../processed_data/parsedNetDelta2020-03.csv","../processed_data/parsedNetDelta2020-04.csv","../processed_data/parsedNetDelta2020-05.csv","../processed_data/parsedNetDelta2020-06.csv","../processed_data/parsedNetDelta2020-07.csv","../processed_data/parsedNetDelta2020-08.csv","../processed_data/parsedNetDelta2020-10.csv","../processed_data/parsedNetDelta2020-11.csv"]
    dataFiles = ["../processed_data//allDataCombined.csv"]
    timestampToData = Dict{String, Float64}()

    for dataFile in dataFiles
        (headers, columns) = readFile(dataFile)
        timestamp = headers[1]
        nope = headers[8]

        for i in 1:length(columns[timestamp])
            ts = columns[timestamp][i]
            np = columns[nope][i]
            if typeof(np)==Float64
                timestampToData[ts] = np
            end

        end
    end
    return timestampToData
end

function getPriceData()
    (priceHeaders, priceColumns) = readFile("../processed_data/priceData.csv")
    timestampToData = Dict{String, Float64}()
    timestamp = priceHeaders[1]
    underlyingPrice = priceHeaders[2]
    for i in 1:length(priceColumns[timestamp])
        ts = priceColumns[timestamp][i]
        up = priceColumns[underlyingPrice][i]
        timestampToData[ts] = up
    end

    return timestampToData
end

function readFile(filePath::String)
    if filePath == ""
        throw(ArgumentError("You must specify a data file"))
    end

    headers = nothing
    columns = nothing
    open(filePath) do openedFile
        (headers, columns) = parseInput!(read(openedFile, String))
    end

    if columns === nothing
        throw(ArgumentError("Something went wrong reading the file"))
    end

    return (headers, columns)
end

function parseInput!(input_data)
    #split the file into lines and store each line as a node object
    lines = split(input_data, '\n')
    headers = split(lines[1], ',')
    columns = Dict{String, Array{Any}}()
    #get the headers
    for h in headers
        columns[h] = Any[]
    end
    #store each row
    for i in 2:length(lines)
        splitLine = split(lines[i], ',')
        if length(splitLine)==1
            break
        end
        #the easy data
        for j in 1:length(columns)
            if tryparse(Float64, splitLine[j])==nothing
                push!(columns[headers[j]],splitLine[j])
            else
                push!(columns[headers[j]],parse(Float64, splitLine[j]))
            end
        end
    end
    return headers, columns
end
