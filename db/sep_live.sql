-- phpMyAdmin SQL Dump
-- version 5.2.0
-- https://www.phpmyadmin.net/
--
-- Host: localhost
-- Generation Time: May 02, 2023 at 07:47 PM
-- Server version: 10.4.27-MariaDB
-- PHP Version: 8.2.0

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `sep_live`
--

-- --------------------------------------------------------

--
-- Table structure for table `activities`
--

CREATE TABLE `activities` (
  `activity_id` int(16) NOT NULL,
  `activity_name` varchar(128) NOT NULL,
  `duration` int(16) NOT NULL,
  `price` float NOT NULL,
  `facility_id` int(16) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `activities`
--

INSERT INTO `activities` (`activity_id`, `activity_name`, `duration`, `price`, `facility_id`) VALUES
(1, 'Swimming pool General use', 1, 2, 1),
(2, 'Swimming pool Lane swimming', 1, 40, 1),
(3, 'Swimming pool Lessons', 1, 2, 1),
(4, 'Swimming pool Team events', 2, 8, 1),
(5, 'Fitness room General use', 1, 5, 2),
(6, 'Squash court 1-hour sessions', 1, 40, 3),
(7, 'Sports hall 1-hour sessions', 1, 3.5, 4),
(8, 'Sports hall Team event', 2, 1.5, 4),
(9, 'Climbing wall General use', 1, 1, 5),
(10, 'Studio Exercise classes', 1, 1, 6);

-- --------------------------------------------------------

--
-- Table structure for table `bookings`
--

CREATE TABLE `bookings` (
  `booking_id` int(16) NOT NULL,
  `user_id` int(16) NOT NULL,
  `activity_id` int(11) NOT NULL,
  `booking_time` datetime NOT NULL,
  `session_id` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `bookings`
--

INSERT INTO `bookings` (`booking_id`, `user_id`, `activity_id`, `booking_time`, `session_id`) VALUES
(210, 1, 4, '2023-04-24 13:00:00', 3),
(211, 1, 10, '2023-04-25 13:00:00', 6),
(212, 1, 7, '2023-05-03 15:30:00', 15),
(213, 1, 7, '2023-05-02 15:30:00', 12),
(214, 1, 3, '2023-05-01 15:30:00', 11);

-- --------------------------------------------------------

--
-- Table structure for table `customers`
--

CREATE TABLE `customers` (
  `customer_id` int(16) NOT NULL,
  `user_id` int(16) NOT NULL,
  `address_id` int(16) NOT NULL,
  `membership_type` int(1) DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `customers`
--

INSERT INTO `customers` (`customer_id`, `user_id`, `address_id`, `membership_type`) VALUES
(1, 1, 1, 0),
(2, 2, 2, 0),
(3, 3, 3, 0);

-- --------------------------------------------------------

--
-- Table structure for table `customer_addresses`
--

CREATE TABLE `customer_addresses` (
  `address_id` int(16) NOT NULL,
  `line_1` varchar(128) NOT NULL,
  `line_2` varchar(128) NOT NULL,
  `city` varchar(128) NOT NULL,
  `postcode` varchar(8) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `customer_addresses`
--

INSERT INTO `customer_addresses` (`address_id`, `line_1`, `line_2`, `city`, `postcode`) VALUES
(1, '1 Main St', 'Westminster', 'London', 'SW1 ABC'),
(2, '2 Main St', 'Westminster', 'London', 'SW1 ABC'),
(3, '3 Main St', 'Westminster', 'London', 'SW1 ABC');

-- --------------------------------------------------------

--
-- Table structure for table `discount`
--

CREATE TABLE `discount` (
  `discount_id` int(16) NOT NULL,
  `discount` int(16) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `discount`
--

INSERT INTO `discount` (`discount_id`, `discount`) VALUES
(1, 15);

-- --------------------------------------------------------

--
-- Table structure for table `employees`
--

CREATE TABLE `employees` (
  `employee_id` int(16) NOT NULL,
  `user_id` int(16) NOT NULL,
  `manager_id` int(16) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `employees`
--

INSERT INTO `employees` (`employee_id`, `user_id`, `manager_id`) VALUES
(1, 4, 1);

-- --------------------------------------------------------

--
-- Table structure for table `facilities`
--

CREATE TABLE `facilities` (
  `facility_id` int(16) NOT NULL,
  `facility_name` varchar(200) NOT NULL,
  `capacity` int(16) NOT NULL,
  `opening_time` time NOT NULL,
  `closing_time` time NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `facilities`
--

INSERT INTO `facilities` (`facility_id`, `facility_name`, `capacity`, `opening_time`, `closing_time`) VALUES
(1, 'Swimming pool', 19, '08:00:00', '20:00:00'),
(2, 'Fitness room', 35, '00:00:00', '00:00:00'),
(3, 'Squash court', 9, '00:00:00', '00:00:00'),
(4, 'Sports hall', 13, '00:00:00', '00:00:00'),
(5, 'Climbing wall', 22, '10:00:00', '20:00:00'),
(6, 'Studio', 25, '00:00:00', '00:00:00');

-- --------------------------------------------------------

--
-- Table structure for table `managers`
--

CREATE TABLE `managers` (
  `manager_id` int(16) NOT NULL,
  `user_id` int(16) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `managers`
--

INSERT INTO `managers` (`manager_id`, `user_id`) VALUES
(1, 5);

-- --------------------------------------------------------

--
-- Table structure for table `sessions`
--

CREATE TABLE `sessions` (
  `session_id` int(16) NOT NULL,
  `activity_id` int(16) NOT NULL,
  `start_date` datetime NOT NULL,
  `end_date` datetime NOT NULL,
  `space_left` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `sessions`
--

INSERT INTO `sessions` (`session_id`, `activity_id`, `start_date`, `end_date`, `space_left`) VALUES
(1, 1, '2023-04-24 10:00:00', '2023-04-24 11:00:00', 30),
(2, 2, '2023-04-24 11:00:00', '2023-04-24 12:00:00', 20),
(3, 4, '2023-04-24 13:00:00', '2023-04-24 16:00:00', 22),
(5, 5, '2023-04-25 10:00:00', '2023-04-25 11:00:00', 40),
(6, 10, '2023-04-25 13:00:00', '2023-04-25 14:00:00', 39),
(7, 6, '2023-04-26 11:00:00', '2023-04-26 12:00:00', 15),
(8, 9, '2023-04-26 15:30:00', '2023-04-26 16:30:00', 17),
(11, 3, '2023-05-01 15:30:00', '2023-05-01 16:30:00', 12),
(12, 7, '2023-05-02 15:30:00', '2023-05-02 16:30:00', 0),
(13, 6, '2023-04-27 11:00:00', '2023-04-27 12:00:00', 24),
(14, 9, '2023-04-27 15:30:00', '2023-04-27 16:30:00', 89),
(15, 7, '2023-05-03 15:30:00', '2023-05-03 16:30:00', 55),
(16, 7, '2023-05-09 15:30:00', '2023-05-09 16:30:00', 0);

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `user_id` int(16) NOT NULL,
  `name_first` varchar(32) DEFAULT NULL,
  `name_last` varchar(32) DEFAULT NULL,
  `email` varchar(128) DEFAULT NULL,
  `password` varchar(128) DEFAULT NULL,
  `salt` varchar(16) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`user_id`, `name_first`, `name_last`, `email`, `password`, `salt`) VALUES
(1, 'Customer1', 'Test', 'customer1@scms.test', '05e52954ae5308bbb28f0e0c0b8147671d1c459c4dbb8aa8ed07623aaa93e7415e90145cb411321000f83caf790ae9ddb3c90d1338f3937bcc8ed10eb5a984c3', 'd44d5041a702bc4f'),
(2, 'Customer2', 'Test', 'customer2@scms.test', '9857fcbe5f4917663b7edb5aafabb27a9d35524e8635ed22ba9f5de379063c6fe38c8bb0a6df10bfe9635fee041cd736e2d657014582af559e9025d03c4a7a2e', 'b3edaae37aea24b9'),
(3, 'Customer3', 'Test', 'customer3@scms.test', 'a2f4e4d4fd7a5dcf2e2e760b3b2e56eda7ad863450e9642627ad55e9c8ad097410c7128ca04a675a94d79ea1a0ae61f7468045a57b5a83e91fb8d7700c0c57fb', '196e7e25cc7a06df'),
(4, 'Employee1', 'Test', 'employee1@scms.test', '5e8a047a9b478ecdaaa12949ddbd3468d9e51d96d982653e332b70281c747953ae85177af94551eca52e9bba06fd77929dbb38fd2b91ac82a727a60de331de4c', 'e02f46cef580d7ef'),
(5, 'Manager1', 'Test', 'manager1@scms.test', '48942946227f3a5f7c325de333831922d58d01ed46a15160115054766c6ef741b2e6077cc3f155650637a3d08543820482835bcbb8650250f74c0a846d91e139', '3e06c618eb4773b1');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `activities`
--
ALTER TABLE `activities`
  ADD PRIMARY KEY (`activity_id`),
  ADD KEY `facility_id` (`facility_id`);

--
-- Indexes for table `bookings`
--
ALTER TABLE `bookings`
  ADD PRIMARY KEY (`booking_id`),
  ADD KEY `user_id` (`user_id`),
  ADD KEY `activity_id` (`activity_id`),
  ADD KEY `session_id` (`session_id`);

--
-- Indexes for table `customers`
--
ALTER TABLE `customers`
  ADD PRIMARY KEY (`customer_id`),
  ADD KEY `user_id` (`user_id`),
  ADD KEY `address_id` (`address_id`);

--
-- Indexes for table `customer_addresses`
--
ALTER TABLE `customer_addresses`
  ADD PRIMARY KEY (`address_id`);

--
-- Indexes for table `discount`
--
ALTER TABLE `discount`
  ADD PRIMARY KEY (`discount_id`);

--
-- Indexes for table `employees`
--
ALTER TABLE `employees`
  ADD PRIMARY KEY (`employee_id`),
  ADD KEY `user_id` (`user_id`),
  ADD KEY `manager_id` (`manager_id`);

--
-- Indexes for table `facilities`
--
ALTER TABLE `facilities`
  ADD PRIMARY KEY (`facility_id`);

--
-- Indexes for table `managers`
--
ALTER TABLE `managers`
  ADD PRIMARY KEY (`manager_id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `sessions`
--
ALTER TABLE `sessions`
  ADD PRIMARY KEY (`session_id`),
  ADD KEY `activity_id` (`activity_id`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`user_id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `activities`
--
ALTER TABLE `activities`
  MODIFY `activity_id` int(16) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

--
-- AUTO_INCREMENT for table `bookings`
--
ALTER TABLE `bookings`
  MODIFY `booking_id` int(16) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=215;

--
-- AUTO_INCREMENT for table `customers`
--
ALTER TABLE `customers`
  MODIFY `customer_id` int(16) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT for table `customer_addresses`
--
ALTER TABLE `customer_addresses`
  MODIFY `address_id` int(16) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT for table `discount`
--
ALTER TABLE `discount`
  MODIFY `discount_id` int(16) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `employees`
--
ALTER TABLE `employees`
  MODIFY `employee_id` int(16) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `facilities`
--
ALTER TABLE `facilities`
  MODIFY `facility_id` int(16) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- AUTO_INCREMENT for table `managers`
--
ALTER TABLE `managers`
  MODIFY `manager_id` int(16) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `sessions`
--
ALTER TABLE `sessions`
  MODIFY `session_id` int(16) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=17;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `user_id` int(16) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `activities`
--
ALTER TABLE `activities`
  ADD CONSTRAINT `activities_ibfk_1` FOREIGN KEY (`facility_id`) REFERENCES `facilities` (`facility_id`);

--
-- Constraints for table `bookings`
--
ALTER TABLE `bookings`
  ADD CONSTRAINT `bookings_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`),
  ADD CONSTRAINT `bookings_ibfk_2` FOREIGN KEY (`activity_id`) REFERENCES `activities` (`activity_id`),
  ADD CONSTRAINT `bookings_ibfk_3` FOREIGN KEY (`session_id`) REFERENCES `sessions` (`session_id`);

--
-- Constraints for table `customers`
--
ALTER TABLE `customers`
  ADD CONSTRAINT `customers_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`),
  ADD CONSTRAINT `customers_ibfk_2` FOREIGN KEY (`address_id`) REFERENCES `customer_addresses` (`address_id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
