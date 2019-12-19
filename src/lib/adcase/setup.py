# Copyright 2019 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Initial app's database setup"""
from lib.adcase import db
from lib.adcase import helper as f

def run():
  """Initial mysql setup.

  Returns:
    ok if successful
  """

  db.query("""CREATE TABLE `users` (
    `id` int NOT NULL AUTO_INCREMENT,
    `email` varchar(255) NOT NULL,
    `status` int NOT NULL,
    `valid_until` date NOT NULL,
    `name` varchar(255) NOT NULL,
    `short_name` varchar(255) NOT NULL,
    PRIMARY KEY (`id`)
    ) ENGINE=InnoDB;""")

  db.query("""CREATE TABLE `analytics` (
    `id` int NOT NULL AUTO_INCREMENT,
    `date` date NOT NULL,
    `year` int NOT NULL,
    `month` int NOT NULL,
    `day` int NOT NULL,
    `dow` int NOT NULL,
    `user_id` int NOT NULL,
    `format` int NOT NULL,
    `action` varchar(255) NOT NULL,
    `qty` int NOT NULL,
    PRIMARY KEY (`id`),
    KEY `user_id` (`user_id`),
    CONSTRAINT `analytics_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
    ) ENGINE=InnoDB;""")

  db.query("""CREATE TABLE `creatives` (
    `id` int NOT NULL AUTO_INCREMENT,
    `user_id` int NOT NULL,
    `file_id` int NOT NULL,
    `format` int NOT NULL,
    `url` varchar(2048) NOT NULL,
    `url_files` text,
    `created_date` datetime DEFAULT NULL,
    PRIMARY KEY (`id`),
    KEY `user_id` (`user_id`),
    CONSTRAINT `creatives_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
    ) ENGINE=InnoDB;""")

  db.query("""CREATE TABLE `sessions` (
    `id` int NOT NULL AUTO_INCREMENT,
    `user_id` int NOT NULL,
    `email` varchar(255) NOT NULL,
    `name` varchar(255) NOT NULL,
    `full` varchar(255) NOT NULL,
    `hash` varchar(2048) NOT NULL,
    `created_date` datetime NOT NULL,
    `enabled` int NOT NULL,
    PRIMARY KEY (`id`)
    ) ENGINE=InnoDB;""")

  db.query("""CREATE TABLE `sizes` (
    `id` int NOT NULL AUTO_INCREMENT,
    `format_id` int NOT NULL,
    `field_name` varchar(255) NOT NULL,
    `data_values` text NOT NULL,
    `user_id` int DEFAULT NULL,
    PRIMARY KEY (`id`),
    KEY `user_id` (`user_id`),
    CONSTRAINT `sizes_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE NO ACTION
    ) ENGINE=InnoDB;""")

  db.query("""INSERT INTO sizes 
    (`id`,`format_id`,`field_name`,`data_values`,`user_id`) 
    VALUES 
    (3,100,'size','160x600,180x70,200x90,220x600,260x600,260x650,260x800,300x125,300x250,300x450,300x600,320x50,320x100,320x480,360x50,360x100,728x90,920x100,920x120,920x170,920x250,920x300,920x350,970x90,970x250,1260x100,1260x120,1260x170,1260x300,1260x350,other',NULL),
    (20,101,'width','728,900,940,950,970',NULL),
    (24,101,'collapsed_height','60,80,90',NULL),
    (26,102,'width','728,900,940,950,970',NULL),
    (27,102,'collapsed_height','60,80,90',NULL),
    (28,102,'expanded_height','200,250,251,270,300',NULL),
    (29,103,'size','800x600,900x600,1040x480,1000x540,1000x680,300x416,300x250,320x480,400x400,328x568,480x320,518x690,500x500,980x642,995x650',NULL),
    (31,104,'size','800x600,900x600,1040x480,1000x540,1000x680,300x416,300x250,320x480,400x400,328x568,480x320,518x690,500x500,980x642,995x650',NULL),
    (32,105,'size','300x250,300x600,920x250,950x200,950x300,360x300,360x100,360x50,300x450,640x360,640x480,300x162',NULL),
    (33,108,'width','970,940,900,728,300,320,1200',NULL),
    (34,108,'collapsed_height','50,60,80,90,100,200',NULL),
    (35,109,'width','728,860,900,970,1000',NULL),
    (36,109,'collapsed_height','60,80,90',NULL),
    (37,109,'expanded_height','200,250,251',NULL),
    (38,110,'width','728,860,900,970,1000',NULL),
    (39,110,'collapsed_height','60,80,90',NULL),
    (40,110,'expanded_height','200,250,251',NULL),
    (41,111,'size','160x600,260x600,260x800,300x125,300x250,300x450,300x600,320x50,360x50,360x100,720x90,970x90,970x250',NULL),
    (42,112,'size','800x600,900x600,1040x480,1000x540,1000x680,300x416,300x250,320x480,328x568,480x320,518x690,500x500,980x642,1280x720    ',NULL),
    (43,115,'width','320,360,728,900,970',NULL),
    (44,115,'inline_height','50,60,80,90,100',NULL),
    (45,115,'sticky_height','50,60,80,90,100',NULL),
    (47,117,'collapsed_size','320x90,970x90',NULL),
    (48,117,'expanded_size','320x250,970x250',NULL),
    (49,118,'collapsed_size','320x90,970x90',NULL),
    (50,118,'expanded_size','320x250,970x250',NULL),
    (51,119,'width','300,320,728,900,970',NULL),
    (52,119,'collapsed_height','50,60,80,90,100',NULL),
    (53,119,'expanded_height','480,600',NULL),
    (54,120,'left_width','120,160,200,300',NULL),
    (55,120,'left_height','300,600,800',NULL),
    (56,120,'center_width','800,1000',NULL),
    (57,120,'center_height','540,600',NULL),
    (59,121,'size','300x250,300x600',NULL),
    (60,121,'expanded_size','400x300,600x400,640x480',NULL),
    (61,122,'creative_size','300x250,300x270,320x250,300x600,1344x270,1115x270,960x270,955x270,795x270,768x270,542x270,320x270',NULL),
    (62,122,'internal_height','600,800,1000,1080',NULL),
    (63,122,'header_height','0,50,60,70,80,100',NULL),
    (64,122,'footer_height','0,50,60,70,80,100',NULL),
    (65,123,'ad_size','300x250,300x600,970x250,320x250',NULL),
    (66,123,'cube_size','100,150,200,250,300',NULL),
    (157,124,'size','800x600,900x600,1040x480,1000x540,1000x680,300x416,300x250,320x480,400x400,328x568,480x320,518x690,500x500,980x642,995x650',NULL),
    (467,125,'width','728,900,940,950,970',NULL),
    (468,125,'collapsed_height','60,80,90',NULL),
    (469,125,'expanded_height','200,250,251,270,300',NULL),
    (471,101,'expanded_height','250,300\r\n\r\n',NULL)
    """)

  return "OK"