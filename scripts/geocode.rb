#!/usr/bin/env ruby

require "net/http"
require "csv"
require "json"

# Usage:
#
# ./scripts/geocode.rb <csv-file>
#
# CSV should have a header row with an "address" column and an optional "zipcode" column.
# Creates a new CSV file which adds four columns to each row: "lat", "lng", "accuracy" and "location_name".
#

BASE_URL = "http://ec2-34-228-58-223.compute-1.amazonaws.com:4000/v1/search?text="
ADDRESS_COLUMN = "address"
ZIP_CODE_COLUMN = "zipcode"

ADDR_REXP = /^(?<num>[\dX\s-]*)(?<blk>BLK)?\s*(?<dir>[NESW])?\.?\s*(?<street>[\w\d\s]+)/
STREET_REXP = /(?<name>[\w\d\s]*)(?<type>(AV|PL|RD|DR|ST|BL))$/
STREET_LOOKUP = {
  "AV" => "AVE",
  "BL" => "BLVD",
  "PL" => "PL",
  "DR" => "DR",
  "ST" => "ST",
  "RD" => "RD",
}

def transform_address(raw)
  addr_data = ADDR_REXP.match(raw)
  return raw if !addr_data

  number = addr_data[:num].gsub("X", "0").split("-").first || ""

  st_match = STREET_REXP.match(addr_data[:street])
  street = st_match ?
    "#{st_match[:name].strip} #{STREET_LOOKUP[st_match[:type]]}" :
    addr_data[:street]

  "#{number} #{addr_data[:dir]} #{street}"
end

# Modifies the given row to add lat/lng as well as extra metadata from pelias
def geocode(row, retry_count=3)
  return if !row

  address = transform_address(row[ADDRESS_COLUMN])

  address += ", #{row[ZIP_CODE_COLUMN]}" if row[ZIP_CODE_COLUMN]

  escaped_address = URI.escape(address)
  resp = Net::HTTP.get(URI.parse("#{BASE_URL}#{escaped_address}"))

  geo = JSON.load(resp)
  loc = geo["features"].first
  if !loc
    puts "No matches for address [#{address}]"
    return
  end

  row["lng"] = loc["geometry"]["coordinates"][0]
  row["lat"] = loc["geometry"]["coordinates"][1]
  row["accuracy"] = loc["properties"]["accuracy"]
  row["location_name"] = loc["properties"]["name"]

  puts "#{address} -> #{row["location_name"]}"
rescue Net::OpenTimeout
  if retry_count > 0 
    puts "TIMEOUT on row #{row.to_h}, retrying"
    geocode(row, retry_count-1)
  else
    puts "TIMEOUT on row #{row.to_h}, no more retries"
  end
end

def dump(table, filename, rows=nil)
  if rows && rows > 0
    puts "dumping first #{rows} rows"
    output = table.headers.to_csv
    output += table.first(rows).map(&:to_csv).join('')
  else
    output = table.to_csv
  end

  File.open(filename, "wb") do |file|
    file.puts(output)
  end
end

def print_help
  puts %(
geocode.rb - Lookup lat/long for a CSV of addresses

  usage: geocode.rb <filename>

Input CSV should have a header row with a column labeled 'address', plus 
optionally a 'zipcode' column. For an input file `locations.csv` the result 
is written to `locations-geocoded.csv`, which includes all columns from the 
input file, plus lat/lng and geocoding metadata columns.

Columns added:
* lat: Latitude in degrees
* lng: Longitude in degrees
* accuracy: The type of location matched: 'point' is a precise point; 
  'centroid' is an entire road, neighborhood, or other shape. Centroids are 
  likely incorrect matches, so you should manually review them or exclude them 
  from your final dataset.
* location_name: A human-readable name for the address, to aid in validating 
  results

In the event of an error, geocode.rb attempts to write completed results to the
output file. When running the command again with the original filename, the 
script checks for an output file and resumes at the last completed entry.

geocode.rb makes requests to CJP's instance of the open source Pelias geocoder.
If its URL changes, update the BASE_URL variable in the script.
  )
end

def run(args=ARGV)
  filename = args[0]
  if filename.nil? || filename.start_with?('-h')
    print_help
    return
  end

  base_filename = filename.gsub(/\.csv$/, "")
  out_filename = "#{base_filename}-geocoded.csv"

  csv_table = CSV.read(filename, headers: true)

  if !csv_table.headers.include?(ADDRESS_COLUMN)
    puts "CSV is not formatted correctly, it needs an 'address' column"
    return
  end

  completed_csv = []
  begin
    completed_csv = CSV.read(out_filename, headers: true)
    puts "Found existing output file #{out_filename} with #{completed_csv.count} lines, resuming"
  rescue Errno::ENOENT => e
    nil
  end

  count = 0
  geocoded_count = 0
  output_table = csv_table.zip(completed_csv).each do |row, completed_result|
    count += 1

    if completed_result
      completed_result.each { |k, v| row[k] = v }
      next
    end

    geocoded_count += 1
    geocode(row)
  end

  puts "geocoded #{geocoded_count} rows, writing #{count} lines to #{out_filename}"

  dump(output_table, out_filename)
rescue Exception => e
  puts "unknown error #{e}"

  dump(csv_table, out_filename, count)
end

run

