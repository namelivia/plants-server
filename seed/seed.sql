--Insert some test plants
INSERT INTO plants (id, name, description, water_every, image, journaling_key, last_watering, indoor) VALUES (1, 'Test plant 1', 'This is test plant 1', 7, 'test_image_1', gen_random_uuid(), '2020-11-07 20:19:30.000000', false);
INSERT INTO plants (id, name, description, water_every, image, journaling_key, last_watering, indoor) VALUES (2, 'Test plant 2', 'This is test plant 2', 7, 'test_image_2', gen_random_uuid(), '2020-11-07 20:19:30.000000', false);
INSERT INTO plants (id, name, description, water_every, image, journaling_key, last_watering, indoor) VALUES (3, 'Test plant 3', 'This is test plant 3', 7, 'test_image_3', gen_random_uuid(), '2020-11-07 20:19:30.000000', true);
