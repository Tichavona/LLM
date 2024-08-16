USE [dbGPT]
GO

CREATE TABLE [dbo].[users](
	[id] [int] IDENTITY(1,1) PRIMARY KEY NOT NULL,
	[email] [nvarchar](255) NOT NULL,
	[first_name] [nvarchar](100) NOT NULL,
	[surname] [nvarchar](100) NOT NULL,
	[mobile_number] [nvarchar](20) NOT NULL,
	[account_number] [nvarchar](50) NULL,
	[department] [nvarchar](100) NULL,
	[profession] [nvarchar](100) NULL,
	[password_hash] [nvarchar](255) NOT NULL,
	[user_type] [nvarchar](50) NOT NULL
);
GO

CREATE TABLE UserLocationData (
    id INT PRIMARY KEY IDENTITY(1,1),
    user_id INT,
    status VARCHAR(10),
    event_time DATETIME,
    geolocation_coordinates VARCHAR(50),
    ip_address VARCHAR(50),
    FOREIGN KEY (user_id) REFERENCES Users(id) -- Assuming you have a Users table
);
