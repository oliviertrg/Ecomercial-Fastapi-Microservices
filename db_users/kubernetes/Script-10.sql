
CREATE TABLE public.users (
	user_id serial4 NOT NULL,
	usersname varchar(50) NULL,
	email varchar(50) NULL,
	passwords varchar NULL,
	is_active bool NULL,
	is_staff bool NULL,
	create_at timestamptz NULL DEFAULT CURRENT_TIMESTAMP,
	CONSTRAINT users_pkey PRIMARY KEY (user_id)
);


