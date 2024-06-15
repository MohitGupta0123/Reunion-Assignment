use v2

Declare @json_table varchar(max)

select @json_table = bulkColumn
from openrowset(bulk
'C:\Users\mgmoh\Desktop\json.json', single_clob)T

select 
ROW_NUMBER() OVER (ORDER BY (SELECT NULL)) AS SerialNo,
tableA.season as Season,
tableA.orchestra as OrchestraName,

tableconcerts.Date as ConcertDate,
tableconcerts.eventType as ConcertEventType,
tableconcerts.Venue as ConcertVenue,
tableconcerts.Location as ConcertLocation,
tableconcerts.Time as ConcertTime,

tableA.programID as ProgramID,

tableworks.workTitle as WorkTitle,
tableworks.conductorName as ConductorName,
tableworks.ID as WorkID,

tablesoloistworks.soloistName as SoloistName,
tablesoloistworks.soloistRoles as SoloistRoles,
tablesoloistworks.soloistInstrument as SoloistInstrument,

tableworks.composerName as ComposerName,
tableworks.movement as Movement,
tableworks.interval as IntervalOrNot,

tableA.id as ID

into ProgramOrganization

from openjson(@json_table)
	with(
		season         varchar(8),
		orchestra      varchar(50),
		concerts       nvarchar(max) as json,
		programID      varchar(6),
		works          nvarchar(max) as json,
		id	           varchar(100)
	) as tableA

cross apply openjson(tableA.concerts)
	with(
		Date		   varchar(30),
		eventType	   varchar(30),
		Venue          varchar(100),
        Location       varchar(100),
        Time		   varchar(8)
	)as tableconcerts

cross apply openjson(tableA.works)
	with(
		workTitle	   varchar(50),
		conductorName  varchar(30),
		ID             varchar(100),
        soloists       nvarchar(max) as json,
        composerName   varchar(50),
		movement	   varchar(50),
		interval	   varchar(10)
	)as tableworks

cross apply openjson(tableworks.soloists)
	with(
		soloistName			varchar(50),
		soloistRoles		varchar(5),
		soloistInstrument   varchar(10)
	) as tablesoloistworks

ALTER TABLE ProgramOrganization
ALTER COLUMN SerialNo int NOT NULL;

ALTER TABLE ProgramOrganization
ADD CONSTRAINT PK_Program_Organization PRIMARY KEY (SerialNo);

-- to see complete json file to table
select * from ProgramOrganization;



-- To check the statistics and relevent informations about table
SELECT 
    c.name AS ColumnName,
    t.name AS DataType,
    c.max_length AS MaxLength,
    c.is_nullable AS IsNullable,
    c.is_identity AS IsIdentity,
    c.column_id AS ColumnID
FROM sys.columns c
JOIN sys.types t ON c.user_type_id = t.user_type_id
WHERE c.object_id = OBJECT_ID('ProgramOrganization');

DECLARE @tableName NVARCHAR(MAX) = 'ProgramOrganization';
DECLARE @sql NVARCHAR(MAX) = '';
DECLARE @columnName NVARCHAR(MAX);
-- Create cursor to iterate through columns
DECLARE columnCursor CURSOR FOR
SELECT COLUMN_NAME
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_NAME = @tableName;

OPEN columnCursor;

FETCH NEXT FROM columnCursor INTO @columnName;

WHILE @@FETCH_STATUS = 0
BEGIN
    SET @sql = @sql + 
    'SELECT ''' + @columnName + ''' AS ColumnName, ' +
    'SUM(CASE WHEN ' + @columnName + ' IS NULL THEN 1 ELSE 0 END) AS NullCount, ' +
    'SUM(CASE WHEN ' + @columnName + ' IS NOT NULL THEN 1 ELSE 0 END) AS NotNullCount ' +
    'FROM ' + @tableName + ' UNION ALL ';

    FETCH NEXT FROM columnCursor INTO @columnName;
END;

CLOSE columnCursor;
DEALLOCATE columnCursor;

-- Remove the last UNION ALL
SET @sql = LEFT(@sql, LEN(@sql) - 10);

-- Execute the dynamically generated SQL
EXEC sp_executesql @sql;



-- To create normailzed tables in database

-- Create Concert table
CREATE TABLE Concert (
    SerialNo INT IDENTITY(1,1) PRIMARY KEY,
    Season VARCHAR(50),
    OrchestraName VARCHAR(100),
    ConcertDate varchar(30),
    ConcertEventType VARCHAR(100),
    ConcertVenue VARCHAR(100),
    ConcertLocation VARCHAR(100),
    ConcertTime VARCHAR(20),
    IntervalOrNot VARCHAR(20)
);

-- Create the new table UniquePrograms
CREATE TABLE Program (
    ProgramID VARCHAR(20) PRIMARY KEY,
    SerialNo INT,
    ConductorName VARCHAR(100),
    -- Add other required columns from ProgramOrganization here
    FOREIGN KEY (SerialNo) REFERENCES Concert(SerialNo)  -- Uncomment if SerialNo is included
);

-- Create Work table
CREATE TABLE Work (
    WorkID VARCHAR(20) PRIMARY KEY,
    ProgramID VARCHAR(20),
    WorkTitle VARCHAR(200),
    ComposerName VARCHAR(100),
    FOREIGN KEY (ProgramID) REFERENCES Program(ProgramID)
);

-- Create Soloist table
CREATE TABLE Soloist (
    SerialNo INT,
    WorkID VARCHAR(20),
    SoloistName VARCHAR(100),
    SoloistRoles VARCHAR(10),
    SoloistInstrument VARCHAR(50),
    FOREIGN KEY (SerialNo) REFERENCES Concert(SerialNo),
    FOREIGN KEY (WorkID) REFERENCES Work(WorkID),
    PRIMARY KEY (SerialNo, SoloistName)  -- Assuming combination of SerialNo and SoloistName is unique per work
);

-- Create Movement table
CREATE TABLE Movement (
    WorkID VARCHAR(20),
    Movement VARCHAR(200),
    FOREIGN KEY (WorkID) REFERENCES Work(WorkID)
);


INSERT INTO Concert ( Season, OrchestraName, ConcertDate, ConcertEventType, ConcertVenue, ConcertLocation, ConcertTime, IntervalOrNot)
SELECT DISTINCT
    Season, OrchestraName, ConcertDate, ConcertEventType, ConcertVenue, ConcertLocation, ConcertTime, IntervalOrNot
FROM ProgramOrganization;

-- Insert unique rows into UniquePrograms
INSERT INTO Program (ProgramID,  ConductorName)
SELECT distinct(ProgramID),  ConductorName
FROM (
    SELECT ProgramID,  ConductorName,
           ROW_NUMBER() OVER (PARTITION BY ProgramID ORDER BY (SELECT NULL)) AS rn
    FROM ProgramOrganization
) AS sub
WHERE rn = 1;

INSERT INTO Work (WorkID, ProgramID, WorkTitle, ComposerName)
SELECT WorkID, ProgramID, WorkTitle, ComposerName
FROM (
    SELECT WorkID, ProgramID, WorkTitle, ComposerName
    FROM ProgramOrganization
    GROUP BY WorkID, ProgramID, WorkTitle, ComposerName
) AS UniqueWorks;

INSERT INTO Soloist (SerialNo, WorkID, SoloistName, SoloistRoles, SoloistInstrument)
SELECT SerialNo, WorkID, SoloistName, SoloistRoles, SoloistInstrument
FROM (
    SELECT SerialNo, WorkID, SoloistName, SoloistRoles, SoloistInstrument
    FROM ProgramOrganization
    WHERE SoloistName IS NOT NULL
    GROUP BY SerialNo, WorkID, SoloistName, SoloistRoles, SoloistInstrument
) AS UniqueSoloists;


INSERT INTO Movement (WorkID, Movement)
SELECT WorkID, Movement
FROM (
    SELECT WorkID, Movement
    FROM ProgramOrganization
    WHERE Movement IS NOT NULL
    GROUP BY WorkID, Movement
) AS UniqueMovements;


select * from ProgramOrganization
