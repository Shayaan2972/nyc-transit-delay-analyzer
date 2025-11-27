create Table if NOT Exists subway_delays(
	id serial PRIMARY key,
	train_line varchar(30),
	alert_message varchar(5000),
	alert_type varchar(300),
	created timestamp,
	updated timestamp
	Constraint unique_alert unique(train_line, alert_message, created)

)
