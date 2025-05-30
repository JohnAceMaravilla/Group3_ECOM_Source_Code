-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: May 29, 2025 at 03:23 AM
-- Server version: 10.4.28-MariaDB
-- PHP Version: 8.2.4

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `fenamaz_ecommerce_db`
--

-- --------------------------------------------------------

--
-- Table structure for table `account_address_info`
--

CREATE TABLE `account_address_info` (
  `address_id` int(11) NOT NULL,
  `house_no` varchar(100) NOT NULL,
  `street` varchar(50) NOT NULL,
  `barangay` varchar(50) NOT NULL,
  `city` varchar(50) NOT NULL,
  `province` varchar(50) NOT NULL,
  `region` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `account_address_info`
--

INSERT INTO `account_address_info` (`address_id`, `house_no`, `street`, `barangay`, `city`, `province`, `region`) VALUES
(1, 'Blk 23 Lot 2', 'Panimbao St', 'San Jose', 'Santa Cruz (Capital)', 'Laguna', 'Region IV-A (CALABARZON)'),
(8, 'Blk 23 Lot 2', 'Malino St', 'Labuin', 'Santa Cruz (Capital)', 'Laguna', 'Region IV-A (CALABARZON)'),
(9, 'Blk 23 Lot 23', 'Kalin St', 'Palasan', 'Santa Cruz (Capital)', 'Laguna', 'Region IV-A (CALABARZON)'),
(10, 'Blk 23 Lot 23', 'Kalang St', 'San Juan', 'Santa Cruz (Capital)', 'Laguna', 'Region IV-A (CALABARZON)'),
(11, '112-B', 'Mabini Street', 'Oogong', 'Santa Cruz (Capital)', 'Laguna', 'Region IV-A (CALABARZON)'),
(12, '45', 'Rizal Avenue', 'Bubukal', 'Santa Cruz (Capital)', 'Laguna', 'Region IV-A (CALABARZON)'),
(13, '16-A', 'Katipunan Ext.', 'Oogong', 'Santa Cruz (Capital)', 'Laguna', 'Region IV-A (CALABARZON)'),
(14, '4', 'Blk 8 Lot', 'San Jose', 'Santa Cruz (Capital)', 'Laguna', 'Region IV-A (CALABARZON)'),
(15, '15', 'Blk 82Lot', 'Patimbao', 'Santa Cruz (Capital)', 'Laguna', 'Region IV-A (CALABARZON)'),
(16, 'h94', 'b124', 'Gatid', 'Santa Cruz (Capital)', 'Laguna', 'Region IV-A (CALABARZON)'),
(17, '4', 'Blk 8 Lot', 'Patimbao', 'Santa Cruz (Capital)', 'Laguna', 'Region IV-A (CALABARZON)'),
(18, 'a-2', 'Blk 84', 'Patimbao', 'Santa Cruz (Capital)', 'Laguna', 'Region IV-A (CALABARZON)'),
(19, 'b-12', 'Blk 12 Lot', 'San Juan (Pob.)', 'Kalayaan', 'Laguna', 'Region IV-A (CALABARZON)'),
(20, '10', 'Blk 812Lot', 'Calios', 'Santa Cruz (Capital)', 'Laguna', 'Region IV-A (CALABARZON)'),
(22, '21', 'Blk 124 Lot', 'Santo Angel Central', 'Santa Cruz (Capital)', 'Laguna', 'Region IV-A (CALABARZON)'),
(23, '24', 'Blk 81 Lot', 'Labuin', 'Santa Cruz (Capital)', 'Laguna', 'Region IV-A (CALABARZON)');

-- --------------------------------------------------------

--
-- Table structure for table `account_business_info`
--

CREATE TABLE `account_business_info` (
  `business_id` int(11) NOT NULL,
  `business_name` varchar(100) NOT NULL,
  `permit_no` varchar(50) NOT NULL,
  `issue_date` date NOT NULL,
  `expiry_date` date NOT NULL,
  `business_location` varchar(100) NOT NULL,
  `permit_pic` varchar(299) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `account_business_info`
--

INSERT INTO `account_business_info` (`business_id`, `business_name`, `permit_no`, `issue_date`, `expiry_date`, `business_location`, `permit_pic`) VALUES
(1, 'Zack Shop', 'BP-2024007', '2023-02-23', '2027-02-23', '', 'y07rQ3AIi2qFHVTpErv6kw_images_2.jpg'),
(2, 'TechHustle PH', 'BP-2024-0011', '2023-01-31', '2025-05-31', '', 'hzx5EPeC3-5pHLRJFJqGmQ_images_2.jpg'),
(3, 'DigitalEase', 'BP-2024-0156', '2024-01-03', '2026-10-29', '', 'Qf7V6gfi_p4-zn5Ag_8fYw_download_1.png'),
(4, 'PinoyGizmo', 'BP-2024-0765', '2025-05-17', '2031-04-24', '', 'Lxv3zBTXg9rVIZ82dypzxQ_images_2.jpg'),
(5, 'GadgetGlow', ' BP-2024-0912', '2025-05-08', '2026-09-15', '', 'atyoPKgc5vi6-ZMdOMjxbQ_images_2.jpg');

-- --------------------------------------------------------

--
-- Table structure for table `account_contact_info`
--

CREATE TABLE `account_contact_info` (
  `contact_id` int(11) NOT NULL,
  `email` varchar(100) NOT NULL,
  `phone` varchar(15) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `account_contact_info`
--

INSERT INTO `account_contact_info` (`contact_id`, `email`, `phone`) VALUES
(1, 'admin@gmail.com', '09905712987'),
(8, 'aechkirkstein@gmail.com', '09581729378'),
(9, 'zackcollins01030523@gmail.com', '09509172391'),
(10, 'johnacemaravilla23@gmail.com', '09509712983'),
(11, 'gomaj84380@nomrista.com', '09171234567'),
(12, 'gisof36159@nomrista.com', '09251234567'),
(13, 'cosew28038@leabro.com', '09081238976'),
(14, 'sixek84036@nomrista.com', '09361234876'),
(15, 'felore9470@leabro.com', '09981234456'),
(16, 'wimoh76875@nomrista.com', '09181236789'),
(17, 'vixep66132@nomrista.com', '09491234111'),
(18, 'keraci2263@nomrista.com', '09091234987'),
(19, 'repofoh976@leabro.com', '09192345678'),
(20, 'secac43907@nomrista.com', '09481234123'),
(22, 'feyebim105@leabro.com', '09181237755'),
(23, 'nafetad280@nomrista.com', '09381234001');

-- --------------------------------------------------------

--
-- Table structure for table `account_login_info`
--

CREATE TABLE `account_login_info` (
  `login_id` int(11) NOT NULL,
  `username` varchar(50) NOT NULL,
  `password` varchar(299) NOT NULL,
  `user_role` enum('Buyer','Seller','Admin','Courier') NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `account_login_info`
--

INSERT INTO `account_login_info` (`login_id`, `username`, `password`, `user_role`) VALUES
(1, 'admin@gmail.com', 'scrypt:32768:8:1$MfFy7qbVgeRtxBeA$85d5e6209e64176426d4dff294d2492794ee6cb18ff256e10fb38f69fe41caaf5c04b7dfaf98d27f2aea2430aa240ba5ea901d8d1fac87d78d820d52a9744842', 'Admin'),
(2, 'aechkirkstein@gmail.com', 'scrypt:32768:8:1$UpqEeeZOxGRJojWm$2aa0be7730c3fc154fdaee124588b0425470d38e10eb8dbf8a40e6c86bed6809ac02bf2d8d10d53974f84dc82d992b492dbc6375be41815188d7962b40788327', 'Buyer'),
(3, 'zackcollins01030523@gmail.com', 'scrypt:32768:8:1$fslWCb1uVzvq5c5g$48f0ef5f97c6ad7b65f4282572922c3b15db7e10f836e9d62cd8300776859d393343775be4d49697d30cc1a1d11ddbeb95ba4ef6cd2df5532ee82bf4c6d5f40f', 'Seller'),
(4, 'johnacemaravilla23@gmail.com', 'scrypt:32768:8:1$9zVpIGmrkYqTOeZ9$722d6b4c95876102c36aeb4fced124e0904b314e03c81ddca671c1f971b8a25989a5a7050e0c3f81a8f92b152e7d132156173c800bc96e07a0a9265fdff7676a', 'Courier'),
(5, 'gomaj84380@nomrista.com', 'scrypt:32768:8:1$DryT43G3IarHjJCg$fc8a0f51388702e2086978be9a03520f86acb7df6f6bb5913cd9241807e85c33efbe07fb574784df6900b55837060bf0e3d86ceb37f058d9ec6fab48522d6c71', 'Buyer'),
(6, 'gisof36159@nomrista.com', 'scrypt:32768:8:1$QMuf3w3IQJEpYite$6080da30380510002218f905d07d8a65686b742782657fedcfbaacbe9dde311a84688b7c13c39726430295be2f2b2af9c302243e44d177eb60e4aa40d75f9cba', 'Buyer'),
(7, 'cosew28038@leabro.com', 'scrypt:32768:8:1$noNJN92xDGf2JraC$a75e606a20a1055b78e39d0938ca703e54f07ce632c3fa664d6cf4e223c374fab6e5d2878f444b9cc2a4c8f93f8daa6f98cee68a99348246fddaf9c7dc395855', 'Buyer'),
(8, 'sixek84036@nomrista.com', 'scrypt:32768:8:1$2T7zZPX9cFf6Jwos$9b62bbd2398750d30d57491780dd8288704d5f4d0700ddc8bc35308c156fc7a6d3e0005ddccdd5b5bde498534336ede596fcf056a1fe095bd049463c5b0c2c92', 'Buyer'),
(9, 'felore9470@leabro.com', 'scrypt:32768:8:1$6Vn2XZGkPguG5OSw$7b570caf5abb1a93e8d9baaeed2da50aa8a34c0c882892ca5f1542c178b231bb627b7754fa473cb8468a010d6a96e78a1317159b16dfc21a180c1fad35063cf2', 'Courier'),
(10, 'wimoh76875@nomrista.com', 'scrypt:32768:8:1$oligZycVIvsy8Wvh$3ff822f7599e48b4d8b301d76c28fc81d6559f5514b0ff151a13bc2d9bac38ff64076bee88775015200f0a0d27eb5a0a0ef1210d74de2b37577439d6cfe4fc4d', 'Courier'),
(11, 'vixep66132@nomrista.com', 'scrypt:32768:8:1$qo7zwBmSaaMtaSIn$de27fddf9fab3cf5b3a9838216aa3d42c08aa3bafca7056c88a629af02ff73e7c9e3a8540fd064b1e049bfb737f183f7039afb8bf1f468698cce7d1ec50959a2', 'Courier'),
(12, 'keraci2263@nomrista.com', 'scrypt:32768:8:1$kjsZ9IkSXi9mfvg4$5348109682227498f8a11cace36d7976a9e7cef6b968f243315136fafa391fffbee820317a80b729f5d344e77a6011f9b791248d737faa78d15456ec09c4abc1', 'Courier'),
(13, 'repofoh976@leabro.com', 'scrypt:32768:8:1$iurs3pdYErE5Y9PT$65f560f377b168cc13617fd71b23ac76bc31de296adab1fcca8e755eed2740969ede48bef34e54f91ec09d117cb6cee274470771d1000b549e0eaf090da2ec11', 'Seller'),
(14, 'secac43907@nomrista.com', 'scrypt:32768:8:1$S3r0nn2sXkRfPTPr$182556ce338df5618b1c83fee2c98fc4d83c9e615aeb07f457517bd83da5a101c53cd7c1cfb30a5f288c8af74f3f2028c6e33e8532d58d49c42fd7878c655efa', 'Seller'),
(15, 'feyebim105@leabro.com', 'scrypt:32768:8:1$LcL5eC3LMG9N2PH7$1472c7f26a6ab431942b55166c9fe8bcbe9d008065589c7dd0e16fb7e98da1172bdcdab270a6a69d7476e94bc044ea52d7ce85d8a35c17a6abbd7413df5e7af0', 'Seller'),
(16, 'nafetad280@nomrista.com', 'scrypt:32768:8:1$IDbhVQ4VoxVvGqcx$c600f55ebb0b76a2935adc8dfc741cc768609812db201122c45cde945ddf64b3ef73c3dda7634a8a6a3752a26a5c1d1bb9c601846bc51921aff6069629a20075', 'Seller');

-- --------------------------------------------------------

--
-- Table structure for table `account_personal_info`
--

CREATE TABLE `account_personal_info` (
  `personal_id` int(11) NOT NULL,
  `firstname` varchar(50) NOT NULL,
  `lastname` varchar(50) NOT NULL,
  `sex` enum('Male','Female') NOT NULL,
  `age` int(11) NOT NULL,
  `birthdate` date NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `account_personal_info`
--

INSERT INTO `account_personal_info` (`personal_id`, `firstname`, `lastname`, `sex`, `age`, `birthdate`) VALUES
(1, 'Cate', 'Fenamaz', 'Male', 34, '1990-08-02'),
(8, 'Aech', 'Kirkstein', 'Male', 23, '2001-08-29'),
(9, 'Zack', 'Collins', 'Male', 24, '2001-02-05'),
(10, 'Ace', 'Maravilla', 'Male', 35, '1990-05-01'),
(11, 'Ana', 'Dela Cruz', 'Female', 24, '2000-05-29'),
(12, 'Mark', 'Reyes', 'Male', 22, '2003-04-29'),
(13, 'Camille', ' Bautista', 'Female', 26, '1999-05-23'),
(14, 'Jericho', 'Santos', 'Male', 25, '2000-05-10'),
(15, 'Carlo', 'Ramirez', 'Male', 25, '2000-04-27'),
(16, 'Maylene', 'Gomez', 'Female', 25, '2000-02-03'),
(17, 'Rico', 'Fernandez', 'Male', 22, '2003-05-03'),
(18, 'Kristine', 'Navarro', 'Female', 26, '1999-04-30'),
(19, 'Miguel', 'Torres', 'Male', 25, '2000-05-03'),
(20, 'Joanna', 'Velasco', 'Female', 25, '2000-05-08'),
(22, 'Paul', 'Gutierrez', 'Male', 25, '2000-05-01'),
(23, 'Erika', 'Mendoza', 'Female', 23, '2002-05-24');

-- --------------------------------------------------------

--
-- Table structure for table `account_valid_info`
--

CREATE TABLE `account_valid_info` (
  `valid_id` int(11) NOT NULL,
  `id_type` varchar(50) NOT NULL,
  `id_no` varchar(50) NOT NULL,
  `id_pic` varchar(299) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `account_valid_info`
--

INSERT INTO `account_valid_info` (`valid_id`, `id_type`, `id_no`, `id_pic`) VALUES
(1, 'Driver\'s License', 'DL878571923', 'CyVqI8SyhgvSggGXcTOGWA_dl_man.jpg'),
(2, 'Driver\'s License', 'DL9051892378912', 'U2s6gKaud0xTesuenJNsKg_dl_man.jpg'),
(3, 'Driver\'s License', 'DL859719823789', 'dr1bDB_aO4nK_s45VAQMEg_dl_man.jpg'),
(4, 'Driver\'s License', 'DL857198023', 'TaQlc3lN4Jdv8mxnGknorw_dl_man.jpg'),
(5, 'UMID', '9812456321', 'D0kPiDRHIugXLB4A7x4dHQ_tin_woman.jpg'),
(6, 'Passport', 'P524812345PH', 'hdo8UF8MkdfA76iGhJeJzQ_dl_man.jpg'),
(7, 'PhilHealth', 'PH9876123456', 'p-pKtMjA_yp7o12w8P693g_tin_man.jpg'),
(8, 'Voter\'s ID', 'VOT-2022-ABCD1234', 'ktzduAi15LZrwyBqxtxTsg_postal_man.jpg'),
(9, 'Driver\'s License', 'DLN-PH-232312345', 'AW3wkIDgOGDCiTeD6Xd6ww_tin_man.jpg'),
(10, 'Driver\'s License', 'DLN-PH-456789123', 'NHkSuicjzqnITib3o73LGw_postal_woman.jpg'),
(11, 'Driver\'s License', 'DLN-PH-123123123', '358hzTmnkA0SK0O6lB2FQQ_postal_man.jpg'),
(12, 'Driver\'s License', 'DLN-PH-984562347', '2u3Oe_PSROhKyQS1NlKS9A_tin_man.jpg'),
(13, 'TIN ID', 'TIN-000987654', 'Aibobsg7sO4N-iw5dkvOlg_dl_man.jpg'),
(14, 'PhilHealth', 'P789123456PH', 'dyH8OFV9HbhVJ0W6g4159Q_images_2.jpg'),
(15, 'UMID', 'UMID-77558899', 'awwvNy89oYBxUk0XFMfFRw_postal_man.jpg'),
(16, 'Voter\'s ID', 'VOT-PH-ERK998877', 'TkIDQnRxLtXRf8y6q2iDNA_tin_woman.jpg');

-- --------------------------------------------------------

--
-- Table structure for table `admin_order_commission`
--

CREATE TABLE `admin_order_commission` (
  `commission_id` int(11) NOT NULL,
  `order_id` int(11) NOT NULL,
  `seller_id` int(11) NOT NULL,
  `commission_rate` decimal(10,2) NOT NULL DEFAULT 8.00,
  `commission_amount` decimal(10,2) NOT NULL CHECK (`commission_amount` >= 0),
  `status` enum('Pending','Paid') NOT NULL DEFAULT 'Pending',
  `date_generated` datetime NOT NULL DEFAULT current_timestamp(),
  `date_paid` datetime DEFAULT NULL,
  `rate_id` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `admin_order_commission`
--

INSERT INTO `admin_order_commission` (`commission_id`, `order_id`, `seller_id`, `commission_rate`, `commission_amount`, `status`, `date_generated`, `date_paid`, `rate_id`) VALUES
(1, 2, 3, 8.00, 1599.92, 'Pending', '2025-05-29 09:09:34', NULL, NULL),
(2, 2, 4, 8.00, 10.32, 'Pending', '2025-05-29 09:09:34', NULL, NULL),
(3, 4, 3, 8.00, 3119.92, 'Pending', '2025-05-29 09:09:39', NULL, NULL),
(4, 4, 4, 8.00, 6.32, 'Pending', '2025-05-29 09:09:39', NULL, NULL),
(5, 5, 3, 8.00, 799.92, 'Pending', '2025-05-29 09:09:42', NULL, NULL),
(6, 5, 4, 8.00, 7.12, 'Pending', '2025-05-29 09:09:42', NULL, NULL),
(7, 6, 3, 8.00, 1519.84, 'Pending', '2025-05-29 09:09:46', NULL, NULL),
(8, 6, 4, 8.00, 5.52, 'Pending', '2025-05-29 09:09:46', NULL, NULL),
(9, 1, 3, 8.00, 999.92, 'Pending', '2025-05-29 09:09:48', NULL, NULL),
(10, 1, 4, 8.00, 6.32, 'Pending', '2025-05-29 09:09:48', NULL, NULL),
(11, 7, 3, 8.00, 5200.00, 'Pending', '2025-05-29 09:15:57', NULL, NULL),
(12, 7, 4, 8.00, 4.72, 'Pending', '2025-05-29 09:15:57', NULL, NULL);

-- --------------------------------------------------------

--
-- Table structure for table `admin_sales`
--

CREATE TABLE `admin_sales` (
  `sales_id` int(11) NOT NULL,
  `admin_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `user_type` enum('Seller','Courier') DEFAULT NULL,
  `order_id` int(11) NOT NULL,
  `total_sales` decimal(10,2) NOT NULL CHECK (`total_sales` >= 0),
  `date_generated` datetime NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `admin_sales`
--

INSERT INTO `admin_sales` (`sales_id`, `admin_id`, `user_id`, `user_type`, `order_id`, `total_sales`, `date_generated`) VALUES
(1, 1, 3, 'Seller', 2, 1599.92, '2025-05-29 09:09:34'),
(2, 1, 4, 'Courier', 2, 10.32, '2025-05-29 09:09:34'),
(3, 1, 3, 'Seller', 4, 3119.92, '2025-05-29 09:09:39'),
(4, 1, 4, 'Courier', 4, 6.32, '2025-05-29 09:09:39'),
(5, 1, 3, 'Seller', 5, 799.92, '2025-05-29 09:09:42'),
(6, 1, 4, 'Courier', 5, 7.12, '2025-05-29 09:09:42'),
(7, 1, 3, 'Seller', 6, 1519.84, '2025-05-29 09:09:46'),
(8, 1, 4, 'Courier', 6, 5.52, '2025-05-29 09:09:46'),
(9, 1, 3, 'Seller', 1, 999.92, '2025-05-29 09:09:48'),
(10, 1, 4, 'Courier', 1, 6.32, '2025-05-29 09:09:48'),
(11, 1, 3, 'Seller', 7, 5200.00, '2025-05-29 09:15:57'),
(12, 1, 4, 'Courier', 7, 4.72, '2025-05-29 09:15:57');

-- --------------------------------------------------------

--
-- Table structure for table `buyer_cart`
--

CREATE TABLE `buyer_cart` (
  `cart_id` int(11) NOT NULL,
  `product_id` int(11) NOT NULL,
  `buyer_id` int(11) NOT NULL,
  `quantity` int(11) NOT NULL CHECK (`quantity` > 0),
  `total_amount` decimal(10,2) NOT NULL CHECK (`total_amount` >= 0),
  `status` enum('On cart','Checked Out') NOT NULL DEFAULT 'On cart',
  `date_added` datetime NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `buyer_cart`
--

INSERT INTO `buyer_cart` (`cart_id`, `product_id`, `buyer_id`, `quantity`, `total_amount`, `status`, `date_added`) VALUES
(1, 25, 2, 1, 12499.00, 'Checked Out', '2025-05-29 08:54:17'),
(2, 22, 2, 1, 19999.00, 'Checked Out', '2025-05-29 09:02:04'),
(3, 5, 2, 1, 45999.00, 'Checked Out', '2025-05-29 09:02:23'),
(4, 4, 2, 1, 38999.00, 'Checked Out', '2025-05-29 09:02:27'),
(5, 13, 2, 1, 9999.00, 'Checked Out', '2025-05-29 09:02:39'),
(6, 15, 2, 2, 18998.00, 'Checked Out', '2025-05-29 09:02:45'),
(11, 8, 2, 2, 65000.00, 'Checked Out', '2025-05-29 09:13:43');

-- --------------------------------------------------------

--
-- Table structure for table `buyer_like`
--

CREATE TABLE `buyer_like` (
  `like_id` int(11) NOT NULL,
  `product_info_id` int(11) NOT NULL,
  `buyer_id` int(11) NOT NULL,
  `status` enum('Liked','Unliked') NOT NULL DEFAULT 'Liked',
  `date_liked` datetime NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `buyer_like`
--

INSERT INTO `buyer_like` (`like_id`, `product_info_id`, `buyer_id`, `status`, `date_liked`) VALUES
(2, 41, 2, 'Liked', '2025-05-29 09:03:45'),
(4, 12, 2, 'Liked', '2025-05-29 09:03:51'),
(5, 10, 2, 'Liked', '2025-05-29 09:04:02');

-- --------------------------------------------------------

--
-- Table structure for table `buyer_order`
--

CREATE TABLE `buyer_order` (
  `order_id` int(11) NOT NULL,
  `shop_id` int(11) NOT NULL,
  `seller_id` int(11) NOT NULL,
  `product_id` int(11) NOT NULL,
  `buyer_id` int(11) NOT NULL,
  `quantity` int(11) NOT NULL CHECK (`quantity` > 0),
  `total_amount` decimal(10,2) NOT NULL CHECK (`total_amount` >= 0),
  `payment_method` enum('Cash on Delivery') NOT NULL,
  `payment_status` enum('Unpaid','Paid') NOT NULL DEFAULT 'Unpaid',
  `status` enum('Pending','To Pack','Packed','Shipping','Shipped','For Delivery','Out for Delivery','Delivered','Received','Rejected') NOT NULL DEFAULT 'Pending',
  `date_ordered` datetime NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `buyer_order`
--

INSERT INTO `buyer_order` (`order_id`, `shop_id`, `seller_id`, `product_id`, `buyer_id`, `quantity`, `total_amount`, `payment_method`, `payment_status`, `status`, `date_ordered`) VALUES
(1, 1, 3, 25, 2, 1, 12578.00, 'Cash on Delivery', 'Paid', 'Received', '2025-05-29 09:04:14'),
(2, 1, 3, 22, 2, 1, 20128.00, 'Cash on Delivery', 'Paid', 'Received', '2025-05-29 09:04:14'),
(3, 1, 3, 5, 2, 1, 46078.00, 'Cash on Delivery', 'Unpaid', 'Packed', '2025-05-29 09:04:14'),
(4, 1, 3, 4, 2, 1, 39078.00, 'Cash on Delivery', 'Paid', 'Received', '2025-05-29 09:04:14'),
(5, 1, 3, 13, 2, 1, 10088.00, 'Cash on Delivery', 'Paid', 'Received', '2025-05-29 09:04:14'),
(6, 1, 3, 15, 2, 2, 19067.00, 'Cash on Delivery', 'Paid', 'Received', '2025-05-29 09:04:14'),
(7, 1, 3, 8, 2, 2, 65059.00, 'Cash on Delivery', 'Paid', 'Received', '2025-05-29 09:13:58');

-- --------------------------------------------------------

--
-- Table structure for table `courier_sales`
--

CREATE TABLE `courier_sales` (
  `sales_id` int(11) NOT NULL,
  `courier_id` int(11) NOT NULL,
  `order_id` int(11) NOT NULL,
  `sale` decimal(10,2) NOT NULL,
  `date_created` datetime NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `courier_sales`
--

INSERT INTO `courier_sales` (`sales_id`, `courier_id`, `order_id`, `sale`, `date_created`) VALUES
(1, 4, 2, 118.68, '2025-05-29 09:09:34'),
(2, 4, 4, 72.68, '2025-05-29 09:09:39'),
(3, 4, 5, 81.88, '2025-05-29 09:09:42'),
(4, 4, 6, 63.48, '2025-05-29 09:09:46'),
(5, 4, 1, 72.68, '2025-05-29 09:09:48'),
(6, 4, 7, 54.28, '2025-05-29 09:15:57');

-- --------------------------------------------------------

--
-- Table structure for table `login_attempts`
--

CREATE TABLE `login_attempts` (
  `id` int(11) NOT NULL,
  `user_id` int(11) DEFAULT NULL,
  `email` varchar(255) DEFAULT NULL,
  `ip_address` varchar(45) DEFAULT NULL,
  `user_type` varchar(50) DEFAULT NULL,
  `status` varchar(20) DEFAULT NULL,
  `timestamp` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `login_attempts`
--

INSERT INTO `login_attempts` (`id`, `user_id`, `email`, `ip_address`, `user_type`, `status`, `timestamp`) VALUES
(1, 1, 'admin@gmail.com', '127.0.0.1', 'Admin', 'success', '2025-05-28 01:53:58'),
(2, 3, 'zackcollins01030523@gmail.com', '127.0.0.1', 'Seller', 'success', '2025-05-28 09:55:21'),
(3, NULL, 'aechkirkstein@gmail.com', '127.0.0.1', NULL, 'failed', '2025-05-28 11:20:23'),
(4, 2, 'aechkirkstein@gmail.com', '127.0.0.1', 'Buyer', 'success', '2025-05-28 11:20:32'),
(5, 13, 'repofoh976@leabro.com', '127.0.0.1', 'Seller', 'success', '2025-05-28 11:23:33'),
(6, 14, 'secac43907@nomrista.com', '127.0.0.1', 'Seller', 'success', '2025-05-28 12:00:59'),
(7, 15, 'feyebim105@leabro.com', '127.0.0.1', 'Seller', 'success', '2025-05-28 12:45:30'),
(8, NULL, 'johnacemaravilla23@gmail.com', '127.0.0.1', NULL, 'failed', '2025-05-28 13:10:28'),
(9, 4, 'johnacemaravilla23@gmail.com', '127.0.0.1', 'Courier', 'success', '2025-05-28 13:10:41'),
(10, 2, 'aechkirkstein@gmail.com', '127.0.0.1', 'Buyer', 'success', '2025-05-28 13:12:28'),
(11, 16, 'nafetad280@nomrista.com', '127.0.0.1', 'Seller', 'success', '2025-05-28 13:32:16'),
(12, 3, 'zackcollins01030523@gmail.com', '127.0.0.1', 'Seller', 'success', '2025-05-28 14:00:28'),
(13, 13, 'repofoh976@leabro.com', '127.0.0.1', 'Seller', 'success', '2025-05-28 14:30:51'),
(14, 2, 'aechkirkstein@gmail.com', '127.0.0.1', 'Buyer', 'success', '2025-05-28 16:02:28'),
(15, 3, 'zackcollins01030523@gmail.com', '127.0.0.1', 'Seller', 'success', '2025-05-29 08:52:03'),
(16, NULL, 'johnacemaravill23@gmail.com', '127.0.0.1', NULL, 'failed', '2025-05-29 08:52:49'),
(17, NULL, 'acemaravilla23@gmail.com', '127.0.0.1', NULL, 'failed', '2025-05-29 08:53:07'),
(18, NULL, 'johnacemaravilla23@gmail.com', '127.0.0.1', NULL, 'failed', '2025-05-29 08:53:31'),
(19, NULL, 'johnacemaravilla23@gmail.com', '127.0.0.1', NULL, 'failed', '2025-05-29 08:53:35'),
(20, 4, 'johnacemaravilla23@gmail.com', '127.0.0.1', 'Courier', 'success', '2025-05-29 08:53:44'),
(21, NULL, 'admin@gmail.com', '127.0.0.1', NULL, 'failed', '2025-05-29 09:19:44'),
(22, 1, 'admin@gmail.com', '127.0.0.1', 'Admin', 'success', '2025-05-29 09:19:56'),
(23, 2, 'aechkirkstein@gmail.com', '127.0.0.1', 'Buyer', 'success', '2025-05-29 09:22:41');

-- --------------------------------------------------------

--
-- Table structure for table `messages`
--

CREATE TABLE `messages` (
  `message_id` int(11) NOT NULL,
  `recipient_id` int(11) NOT NULL,
  `sender_id` int(11) NOT NULL,
  `message` text NOT NULL,
  `status` enum('Sent','Delivered','Read') DEFAULT 'Sent',
  `created_at` datetime NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `notifications`
--

CREATE TABLE `notifications` (
  `notification_id` int(11) NOT NULL,
  `recipient_id` int(11) NOT NULL,
  `sender_id` int(11) DEFAULT NULL,
  `notification_type` varchar(100) NOT NULL,
  `notification_title` varchar(100) NOT NULL,
  `content` text NOT NULL,
  `status` enum('Unread','Read') DEFAULT 'Unread',
  `created_at` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `notifications`
--

INSERT INTO `notifications` (`notification_id`, `recipient_id`, `sender_id`, `notification_type`, `notification_title`, `content`, `status`, `created_at`) VALUES
(1, 1, 1, 'Account Registration', 'New Buyer Registration - Cate Fenamaz', 'A new buyer has successfully registered and is waiting for your approval. Check Now!', 'Read', '2025-05-27 20:34:35'),
(2, 1, 1, 'Account Registration', 'Registration Success', 'Congratulations! 🎉 Your buyer account registration has been created successfully. You can now explore a wide range of the latest products in technology, gadgets, and more.', 'Read', '2025-05-27 20:34:35'),
(3, 1, 2, 'Account Registration', 'New Buyer Registration - Aech Kirkstein', 'A new buyer has successfully registered and is waiting for your approval. Check Now!', 'Read', '2025-05-27 20:38:22'),
(4, 2, 1, 'Account Registration', 'Registration Success', 'Congratulations! 🎉 Your buyer account registration has been created successfully. You can now explore a wide range of the latest products in technology, gadgets, and more.', 'Read', '2025-05-27 20:38:22'),
(5, 1, 3, 'Account Registration', 'New Seller Registration - Zack Collins', 'A new seller has successfully registered and is waiting for your approval. Check Now!', 'Read', '2025-05-27 20:40:32'),
(6, 1, 4, 'Account Registration', 'New Courier Registration - Ace Maravilla', 'A new courier has successfully registered and is waiting for your approval. Check Now!', 'Read', '2025-05-27 20:42:19'),
(7, 1, 5, 'Account Registration', 'New Buyer Registration - Ana Dela Cruz', 'A new buyer has successfully registered and is waiting for your approval. Check Now!', 'Read', '2025-05-28 02:08:00'),
(8, 5, 1, 'Account Registration', 'Registration Success', 'Congratulations! 🎉 Your buyer account registration has been created successfully. You can now explore a wide range of the latest products in technology, gadgets, and more.', 'Unread', '2025-05-28 02:08:00'),
(9, 1, 6, 'Account Registration', 'New Buyer Registration - Mark Reyes', 'A new buyer has successfully registered and is waiting for your approval. Check Now!', 'Read', '2025-05-28 02:11:39'),
(10, 6, 1, 'Account Registration', 'Registration Success', 'Congratulations! 🎉 Your buyer account registration has been created successfully. You can now explore a wide range of the latest products in technology, gadgets, and more.', 'Unread', '2025-05-28 02:11:39'),
(11, 1, 7, 'Account Registration', 'New Buyer Registration - Camille  Bautista', 'A new buyer has successfully registered and is waiting for your approval. Check Now!', 'Read', '2025-05-28 02:14:17'),
(12, 7, 1, 'Account Registration', 'Registration Success', 'Congratulations! 🎉 Your buyer account registration has been created successfully. You can now explore a wide range of the latest products in technology, gadgets, and more.', 'Unread', '2025-05-28 02:14:17'),
(13, 1, 8, 'Account Registration', 'New Buyer Registration - Jericho Santos', 'A new buyer has successfully registered and is waiting for your approval. Check Now!', 'Read', '2025-05-28 02:17:23'),
(14, 8, 1, 'Account Registration', 'Registration Success', 'Congratulations! 🎉 Your buyer account registration has been created successfully. You can now explore a wide range of the latest products in technology, gadgets, and more.', 'Unread', '2025-05-28 02:17:23'),
(15, 1, 9, 'Account Registration', 'New Courier Registration - Carlo Ramirez', 'A new courier has successfully registered and is waiting for your approval. Check Now!', 'Read', '2025-05-28 02:21:00'),
(16, 1, 10, 'Account Registration', 'New Courier Registration - Maylene Gomez', 'A new courier has successfully registered and is waiting for your approval. Check Now!', 'Read', '2025-05-28 02:23:18'),
(17, 1, 11, 'Account Registration', 'New Courier Registration - Rico Fernandez', 'A new courier has successfully registered and is waiting for your approval. Check Now!', 'Read', '2025-05-28 02:26:43'),
(18, 1, 12, 'Account Registration', 'New Courier Registration - Kristine Navarro', 'A new courier has successfully registered and is waiting for your approval. Check Now!', 'Read', '2025-05-28 02:28:50'),
(19, 1, 13, 'Account Registration', 'New Seller Registration - Miguel Torres', 'A new seller has successfully registered and is waiting for your approval. Check Now!', 'Read', '2025-05-28 02:34:28'),
(20, 1, 14, 'Account Registration', 'New Seller Registration - Joanna Velasco', 'A new seller has successfully registered and is waiting for your approval. Check Now!', 'Read', '2025-05-28 02:44:38'),
(21, 1, 15, 'Account Registration', 'New Seller Registration - Paul Gutierrez', 'A new seller has successfully registered and is waiting for your approval. Check Now!', 'Read', '2025-05-28 02:53:14'),
(22, 1, 16, 'Account Registration', 'New Seller Registration - Erika Mendoza', 'A new seller has successfully registered and is waiting for your approval. Check Now!', 'Read', '2025-05-28 03:03:06'),
(23, 3, 1, 'Account Registration', 'Account Approved', 'Congratulations! 🎉 Your seller account has been approved. You can now start managing your shop and selling your products.', 'Read', '2025-05-28 03:05:39'),
(24, 13, 1, 'Account Registration', 'Account Approved', 'Congratulations! 🎉 Your seller account has been approved. You can now start managing your shop and selling your products.', 'Read', '2025-05-28 03:05:41'),
(25, 14, 1, 'Account Registration', 'Account Approved', 'Congratulations! 🎉 Your seller account has been approved. You can now start managing your shop and selling your products.', 'Read', '2025-05-28 03:05:43'),
(26, 15, 1, 'Account Registration', 'Account Approved', 'Congratulations! 🎉 Your seller account has been approved. You can now start managing your shop and selling your products.', 'Unread', '2025-05-28 03:05:46'),
(27, 16, 1, 'Account Registration', 'Account Approved', 'Congratulations! 🎉 Your seller account has been approved. You can now start managing your shop and selling your products.', 'Unread', '2025-05-28 03:05:48'),
(28, 4, 1, 'Account Registration', 'Account Approved', 'Your courier account has been approved! You can now start accepting delivery requests.', 'Unread', '2025-05-28 03:06:01'),
(29, 9, 1, 'Account Registration', 'Account Approved', 'Your courier account has been approved! You can now start accepting delivery requests.', 'Unread', '2025-05-28 03:06:03'),
(30, 10, 1, 'Account Registration', 'Account Approved', 'Your courier account has been approved! You can now start accepting delivery requests.', 'Unread', '2025-05-28 03:06:06'),
(31, 11, 1, 'Account Registration', 'Account Approved', 'Your courier account has been approved! You can now start accepting delivery requests.', 'Unread', '2025-05-28 03:06:08'),
(32, 12, 1, 'Account Registration', 'Account Approved', 'Your courier account has been approved! You can now start accepting delivery requests.', 'Unread', '2025-05-28 03:06:10'),
(33, 3, 1, 'New Product', 'New Product Added!', 'Your product **Samsung Galaxy A55 5G** has been successfully added to your inventory.', 'Read', '2025-05-28 10:08:36'),
(34, 3, 1, 'New Product', 'New Product Added!', 'Your product **Acer Aspire 7 Gaming Laptop (2024)** has been successfully added to your inventory.', 'Read', '2025-05-28 10:14:24'),
(36, 3, 1, 'New Product', 'New Product Added!', 'Your product **Intel Core i5 Pro Gaming Tower (Bundle Set)** has been successfully added to your inventory.', 'Read', '2025-05-28 10:27:24'),
(37, 3, 1, 'New Product', 'New Product Added!', 'Your product **realme Note 50** has been successfully added to your inventory.', 'Read', '2025-05-28 10:35:54'),
(38, 3, 1, 'New Product', 'New Product Added!', 'Your product **Xiaomi Redmi Note 13 5G** has been successfully added to your inventory.', 'Read', '2025-05-28 10:42:12'),
(39, 3, 1, 'New Product', 'New Product Added!', 'Your product **Infinix Zero 30 4G** has been successfully added to your inventory.', 'Read', '2025-05-28 10:46:42'),
(40, 3, 1, 'New Product', 'New Product Added!', 'Your product **Tecno Spark 20 Pro** has been successfully added to your inventory.', 'Read', '2025-05-28 11:01:42'),
(41, 3, 1, 'New Product', 'New Product Added!', 'Your product **HONOR X8b** has been successfully added to your inventory.', 'Read', '2025-05-28 11:05:30'),
(42, 3, 1, 'New Product', 'New Product Added!', 'Your product **POCO X6 Pro 5G** has been successfully added to your inventory.', 'Read', '2025-05-28 11:08:19'),
(43, 3, 1, 'New Product', 'New Product Added!', 'Your product **Vivo Y100** has been successfully added to your inventory.', 'Read', '2025-05-28 11:11:31'),
(44, 13, 1, 'New Product', 'New Product Added!', 'Your product **Acer Aspire 3 Slim** has been successfully added to your inventory.', 'Read', '2025-05-28 11:29:08'),
(45, 13, 1, 'New Product', 'New Product Added!', 'Your product **Lenovo IdeaPad Slim 3** has been successfully added to your inventory.', 'Read', '2025-05-28 11:37:12'),
(46, 13, 1, 'New Product', 'New Product Added!', 'Your product **MSI Modern 14** has been successfully added to your inventory.', 'Read', '2025-05-28 11:42:48'),
(47, 13, 1, 'New Product', 'New Product Added!', 'Your product **Apple MacBook Air M1** has been successfully added to your inventory.', 'Read', '2025-05-28 11:49:27'),
(48, 13, 1, 'New Product', 'New Product Added!', 'Your product **Huawei MateBook D14** has been successfully added to your inventory.', 'Read', '2025-05-28 11:52:18'),
(49, 13, 1, 'New Product', 'New Product Added!', 'Your product **Dell Inspiron 14 5430** has been successfully added to your inventory.', 'Read', '2025-05-28 11:56:41'),
(50, 13, 1, 'New Product', 'New Product Added!', 'Your product **Gigabyte G5 KF Gaming Laptop** has been successfully added to your inventory.', 'Read', '2025-05-28 12:00:03'),
(51, 14, 1, 'New Product', 'New Product Added!', 'Your product **ASUS S500SC Desktop Tower** has been successfully added to your inventory.', 'Read', '2025-05-28 12:05:30'),
(52, 14, 1, 'New Product', 'New Product Added!', 'Your product **Dell Inspiron 3020** has been successfully added to your inventory.', 'Read', '2025-05-28 12:09:13'),
(53, 14, 1, 'New Product', 'New Product Added!', 'Your product **HP Pavilion TP01** has been successfully added to your inventory.', 'Read', '2025-05-28 12:12:06'),
(54, 14, 1, 'New Product', 'New Product Added!', 'Your product **Lenovo IdeaCentre 3** has been successfully added to your inventory.', 'Read', '2025-05-28 12:15:01'),
(55, 14, 1, 'New Product', 'New Product Added!', 'Your product **MSI PRO DP21 Mini PC** has been successfully added to your inventory.', 'Read', '2025-05-28 12:17:13'),
(56, 14, 1, 'New Product', 'New Product Added!', 'Your product **Gigabyte Brix Ultra-Compact PC** has been successfully added to your inventory.', 'Read', '2025-05-28 12:19:08'),
(57, 14, 1, 'New Product', 'New Product Added!', 'Your product **Ryzen Budget Gamer** has been successfully added to your inventory.', 'Read', '2025-05-28 12:25:01'),
(58, 14, 1, 'New Product', 'New Product Added!', 'Your product **Intel i7 Performance Tower** has been successfully added to your inventory.', 'Read', '2025-05-28 12:28:54'),
(59, 15, 1, 'New Product', 'New Product Added!', 'Your product **JBL Quantum 100 Gaming Headset** has been successfully added to your inventory.', 'Unread', '2025-05-28 12:52:58'),
(60, 15, 1, 'New Product', 'New Product Added!', 'Your product **Sony WH-CH520 Wireless Headphones** has been successfully added to your inventory.', 'Unread', '2025-05-28 12:56:18'),
(61, 15, 1, 'New Product', 'New Product Added!', 'Your product **Marshall Emberton II Bluetooth Speaker** has been successfully added to your inventory.', 'Unread', '2025-05-28 13:02:05'),
(62, 15, 1, 'New Product', 'New Product Added!', 'Your product **Maono AU-PM421 Condenser Microphone** has been successfully added to your inventory.', 'Unread', '2025-05-28 13:05:25'),
(63, 15, 1, 'New Product', 'New Product Added!', 'Your product **Sennheiser HD 560S Open-Back Headphones** has been successfully added to your inventory.', 'Unread', '2025-05-28 13:08:23'),
(64, 15, 1, 'New Product', 'New Product Added!', 'Your product **Edifier R1280DB Powered Bookshelf Speakers** has been successfully added to your inventory.', 'Unread', '2025-05-28 13:18:01'),
(65, 15, 1, 'New Product', 'New Product Added!', 'Your product **Logitech G435 LIGHTSPEED Wireless Gaming Headset** has been successfully added to your inventory.', 'Unread', '2025-05-28 13:22:13'),
(66, 15, 1, 'New Product', 'New Product Added!', 'Your product **RODE NT1 5th Gen Studio Microphone** has been successfully added to your inventory.', 'Unread', '2025-05-28 13:26:05'),
(67, 16, 1, 'New Product', 'New Product Added!', 'Your product **Logitech C920 HD Pro Webcam** has been successfully added to your inventory.', 'Unread', '2025-05-28 13:36:53'),
(68, 16, 1, 'New Product', 'New Product Added!', 'Your product **Sony ZV-1F Vlog Camera** has been successfully added to your inventory.', 'Unread', '2025-05-28 13:39:47'),
(69, 16, 1, 'New Product', 'New Product Added!', 'Your product **GoPro HERO11 Black** has been successfully added to your inventory.', 'Unread', '2025-05-28 13:42:36'),
(70, 16, 1, 'New Product', 'New Product Added!', 'Your product **Canon EOS M50 Mark II Mirrorless Camera** has been successfully added to your inventory.', 'Unread', '2025-05-28 13:44:52'),
(71, 16, 1, 'New Product', 'New Product Added!', 'Your product **Insta360 X3 360 Action Camera** has been successfully added to your inventory.', 'Unread', '2025-05-28 13:48:24'),
(72, 16, 1, 'New Product', 'New Product Added!', 'Your product **Elgato Cam Link 4K** has been successfully added to your inventory.', 'Unread', '2025-05-28 13:50:21'),
(73, 16, 1, 'New Product', 'New Product Added!', 'Your product **DJI Pocket 2 Creator Combo** has been successfully added to your inventory.', 'Unread', '2025-05-28 13:52:48'),
(74, 16, 1, 'New Product', 'New Product Added!', 'Your product **AverMedia PW513 4K Webcam** has been successfully added to your inventory.', 'Unread', '2025-05-28 13:54:55'),
(75, 3, 1, 'New Product', 'New Product Added!', 'Your product **Google Nest Hub (2nd Gen)** has been successfully added to your inventory.', 'Read', '2025-05-28 14:02:26'),
(76, 3, 1, 'New Product', 'New Product Added!', 'Your product **Xiaomi Smart Door Lock Pro** has been successfully added to your inventory.', 'Read', '2025-05-28 14:04:36'),
(77, 3, 1, 'New Product', 'New Product Added!', 'Your product **Amazon Echo Dot (5th Gen)** has been successfully added to your inventory.', 'Read', '2025-05-28 14:06:52'),
(78, 3, 1, 'New Product', 'New Product Added!', 'Your product **Xiaomi Mi Smart Temperature & Humidity Monitor Clock** has been successfully added to your inventory.', 'Read', '2025-05-28 14:08:20'),
(79, 3, 1, 'New Product', 'New Product Added!', 'Your product **Samsung SmartThings Motion Sensor** has been successfully added to your inventory.', 'Read', '2025-05-28 14:09:53'),
(80, 3, 1, 'New Product', 'New Product Added!', 'Your product **Smart IR/RF Controller** has been successfully added to your inventory.', 'Read', '2025-05-28 14:12:52'),
(81, 3, 1, 'New Product', 'New Product Added!', 'Your product **Philips Hue White & Color Ambiance Bulb (E27)** has been successfully added to your inventory.', 'Read', '2025-05-28 14:15:15'),
(82, 3, 1, 'New Product', 'New Product Added!', 'Your product **TP-Link Tapo C210 Smart Security Camera** has been successfully added to your inventory.', 'Read', '2025-05-28 14:17:23'),
(83, 13, 1, 'New Product', 'New Product Added!', 'Your product **Canon EOS R10 Mirrorless Camera** has been successfully added to your inventory.', 'Read', '2025-05-28 14:33:14'),
(84, 13, 1, 'New Product', 'New Product Added!', 'Your product **Nikon Z50 Mirrorless Camera** has been successfully added to your inventory.', 'Read', '2025-05-28 14:35:51'),
(85, 13, 1, 'New Product', 'New Product Added!', 'Your product **Fujifilm X-T30 II Mirrorless Camera** has been successfully added to your inventory.', 'Read', '2025-05-28 14:39:34'),
(86, 2, 1, 'Order Confirmation', 'Order Placed Successfully', 'Your order has been placed successfully. Orders will be processed soon.', 'Read', '2025-05-29 09:04:14'),
(87, 3, 1, 'New Order', 'New Order Received - Aech Kirkstein', 'Aech Kirkstein has placed an order for: Vivo Y100, POCO X6 Pro 5G, Acer Aspire 7 Gaming Laptop (2024) and 3 more items. Please check your orders section to process the order.', 'Read', '2025-05-29 09:04:14'),
(88, 2, 1, 'Order Update', 'Order Approved', 'Your order for Infinix Zero 30 4G has been approved and is now being prepared for packing.', 'Read', '2025-05-29 09:06:20'),
(89, 2, 1, 'Order Update', 'Order Approved', 'Your order for Xiaomi Redmi Note 13 5G has been approved and is now being prepared for packing.', 'Read', '2025-05-29 09:06:22'),
(90, 2, 1, 'Order Update', 'Order Approved', 'Your order for Acer Aspire 7 Gaming Laptop (2024) has been approved and is now being prepared for packing.', 'Read', '2025-05-29 09:06:24'),
(91, 2, 1, 'Order Update', 'Order Approved', 'Your order for Acer Aspire 7 Gaming Laptop (2024) has been approved and is now being prepared for packing.', 'Read', '2025-05-29 09:06:25'),
(92, 2, 1, 'Order Update', 'Order Approved', 'Your order for POCO X6 Pro 5G has been approved and is now being prepared for packing.', 'Read', '2025-05-29 09:06:26'),
(93, 2, 1, 'Order Update', 'Order Approved', 'Your order for Vivo Y100 has been approved and is now being prepared for packing.', 'Read', '2025-05-29 09:06:29'),
(94, 2, 1, 'Order Update', 'Order Packed', 'Your order for Infinix Zero 30 4G has been packed and is ready for shipment.', 'Read', '2025-05-29 09:06:33'),
(95, 2, 1, 'Order Update', 'Order in Shipping', 'Your order for Infinix Zero 30 4G has been handed off to Standard Shipping and is now in shipping process.', 'Read', '2025-05-29 09:06:35'),
(96, 2, 1, 'Order Update', 'Order Packed', 'Your order for Xiaomi Redmi Note 13 5G has been packed and is ready for shipment.', 'Read', '2025-05-29 09:06:38'),
(97, 2, 1, 'Order Update', 'Order in Shipping', 'Your order for Xiaomi Redmi Note 13 5G has been handed off to Standard Shipping and is now in shipping process.', 'Read', '2025-05-29 09:06:40'),
(98, 2, 1, 'Order Update', 'Order Packed', 'Your order for Acer Aspire 7 Gaming Laptop (2024) has been packed and is ready for shipment.', 'Read', '2025-05-29 09:06:44'),
(99, 2, 1, 'Order Update', 'Order in Shipping', 'Your order for Acer Aspire 7 Gaming Laptop (2024) has been handed off to Standard Shipping and is now in shipping process.', 'Read', '2025-05-29 09:06:46'),
(100, 2, 1, 'Order Update', 'Order Packed', 'Your order for Acer Aspire 7 Gaming Laptop (2024) has been packed and is ready for shipment.', 'Read', '2025-05-29 09:06:49'),
(101, 2, 1, 'Order Update', 'Order Packed', 'Your order for Vivo Y100 has been packed and is ready for shipment.', 'Read', '2025-05-29 09:06:54'),
(102, 2, 1, 'Order Update', 'Order in Shipping', 'Your order for Vivo Y100 has been handed off to Standard Shipping and is now in shipping process.', 'Read', '2025-05-29 09:06:57'),
(103, 2, 1, 'Order Update', 'Order Packed', 'Your order for POCO X6 Pro 5G has been packed and is ready for shipment.', 'Read', '2025-05-29 09:07:01'),
(104, 2, 1, 'Order Update', 'Order in Shipping', 'Your order for POCO X6 Pro 5G has been handed off to Standard Shipping and is now in shipping process.', 'Read', '2025-05-29 09:07:07'),
(105, 2, 1, 'Order Update', 'Order Shipped', 'Your order for Infinix Zero 30 4G has been shipped and is on its way to you.', 'Read', '2025-05-29 09:07:10'),
(106, 2, 1, 'Order Update', 'Order Shipped', 'Your order for Xiaomi Redmi Note 13 5G has been shipped and is on its way to you.', 'Read', '2025-05-29 09:07:12'),
(107, 2, 1, 'Order Update', 'Order Shipped', 'Your order for Acer Aspire 7 Gaming Laptop (2024) has been shipped and is on its way to you.', 'Read', '2025-05-29 09:07:13'),
(108, 2, 1, 'Order Update', 'Order Shipped', 'Your order for POCO X6 Pro 5G has been shipped and is on its way to you.', 'Read', '2025-05-29 09:07:15'),
(109, 2, 1, 'Order Update', 'Order Shipped', 'Your order for Vivo Y100 has been shipped and is on its way to you.', 'Read', '2025-05-29 09:07:16'),
(110, 2, 1, 'Order Update', 'Courier Assigned', 'Your order #6 for Infinix Zero 30 4G has been assigned to courier Ace Maravilla and is awaiting acceptance for delivery.', 'Read', '2025-05-29 09:07:21'),
(111, 4, 1, 'Delivery Assignment', 'New Delivery Assignment - Order #6', 'You have been assigned to deliver Order #6 for Infinix Zero 30 4G to Aech Kirkstein. Please accept or decline this delivery assignment within 8 hours.', 'Unread', '2025-05-29 09:07:21'),
(112, 2, 1, 'Order Update', 'Courier Assigned', 'Your order #5 for Xiaomi Redmi Note 13 5G has been assigned to courier Ace Maravilla and is awaiting acceptance for delivery.', 'Read', '2025-05-29 09:07:24'),
(113, 4, 1, 'Delivery Assignment', 'New Delivery Assignment - Order #5', 'You have been assigned to deliver Order #5 for Xiaomi Redmi Note 13 5G to Aech Kirkstein. Please accept or decline this delivery assignment within 8 hours.', 'Unread', '2025-05-29 09:07:24'),
(114, 2, 1, 'Order Update', 'Courier Assigned', 'Your order #4 for Acer Aspire 7 Gaming Laptop (2024) has been assigned to courier Ace Maravilla and is awaiting acceptance for delivery.', 'Read', '2025-05-29 09:07:27'),
(115, 4, 1, 'Delivery Assignment', 'New Delivery Assignment - Order #4', 'You have been assigned to deliver Order #4 for Acer Aspire 7 Gaming Laptop (2024) to Aech Kirkstein. Please accept or decline this delivery assignment within 8 hours.', 'Unread', '2025-05-29 09:07:27'),
(116, 2, 1, 'Order Update', 'Courier Assigned', 'Your order #2 for POCO X6 Pro 5G has been assigned to courier Ace Maravilla and is awaiting acceptance for delivery.', 'Read', '2025-05-29 09:07:32'),
(117, 4, 1, 'Delivery Assignment', 'New Delivery Assignment - Order #2', 'You have been assigned to deliver Order #2 for POCO X6 Pro 5G to Aech Kirkstein. Please accept or decline this delivery assignment within 8 hours.', 'Unread', '2025-05-29 09:07:32'),
(118, 2, 1, 'Order Update', 'Courier Assigned', 'Your order #1 for Vivo Y100 has been assigned to courier Ace Maravilla and is awaiting acceptance for delivery.', 'Read', '2025-05-29 09:07:34'),
(119, 4, 1, 'Delivery Assignment', 'New Delivery Assignment - Order #1', 'You have been assigned to deliver Order #1 for Vivo Y100 to Aech Kirkstein. Please accept or decline this delivery assignment within 8 hours.', 'Unread', '2025-05-29 09:07:34'),
(120, 2, 1, 'Delivery Update', 'Order Out for Delivery', 'Great news! Your order #1 for Vivo Y100 is now out for delivery with courier  .', 'Read', '2025-05-29 09:07:42'),
(121, 3, 1, 'Delivery Update', 'Order Out for Delivery', 'Order #1 for Vivo Y100 has been accepted by courier   and is now out for delivery to Aech Kirkstein.', 'Read', '2025-05-29 09:07:42'),
(122, 2, 1, 'Delivery Update', 'Order Out for Delivery', 'Great news! Your order #2 for POCO X6 Pro 5G is now out for delivery with courier  .', 'Read', '2025-05-29 09:07:44'),
(123, 3, 1, 'Delivery Update', 'Order Out for Delivery', 'Order #2 for POCO X6 Pro 5G has been accepted by courier   and is now out for delivery to Aech Kirkstein.', 'Read', '2025-05-29 09:07:44'),
(124, 2, 1, 'Delivery Update', 'Order Out for Delivery', 'Great news! Your order #4 for Acer Aspire 7 Gaming Laptop (2024) is now out for delivery with courier  .', 'Read', '2025-05-29 09:07:46'),
(125, 3, 1, 'Delivery Update', 'Order Out for Delivery', 'Order #4 for Acer Aspire 7 Gaming Laptop (2024) has been accepted by courier   and is now out for delivery to Aech Kirkstein.', 'Read', '2025-05-29 09:07:46'),
(126, 2, 1, 'Delivery Update', 'Order Out for Delivery', 'Great news! Your order #5 for Xiaomi Redmi Note 13 5G is now out for delivery with courier  .', 'Read', '2025-05-29 09:07:48'),
(127, 3, 1, 'Delivery Update', 'Order Out for Delivery', 'Order #5 for Xiaomi Redmi Note 13 5G has been accepted by courier   and is now out for delivery to Aech Kirkstein.', 'Read', '2025-05-29 09:07:48'),
(128, 2, 1, 'Delivery Update', 'Order Out for Delivery', 'Great news! Your order #6 for Infinix Zero 30 4G is now out for delivery with courier  .', 'Read', '2025-05-29 09:07:49'),
(129, 3, 1, 'Delivery Update', 'Order Out for Delivery', 'Order #6 for Infinix Zero 30 4G has been accepted by courier   and is now out for delivery to Aech Kirkstein.', 'Read', '2025-05-29 09:07:49'),
(130, 2, 1, 'Order Complete', 'Order Delivered & Payment Confirmed', 'Your order #1 for Vivo Y100 has been successfully delivered and payment has been confirmed. Thank you for your purchase!', 'Read', '2025-05-29 09:07:53'),
(131, 3, 1, 'Order Complete', 'Order Delivered & Payment Confirmed', 'Order #1 for Vivo Y100 has been successfully delivered to Aech Kirkstein by courier  . Payment has been confirmed and the order is now complete.', 'Read', '2025-05-29 09:07:53'),
(132, 2, 1, 'Order Complete', 'Order Delivered & Payment Confirmed', 'Your order #2 for POCO X6 Pro 5G has been successfully delivered and payment has been confirmed. Thank you for your purchase!', 'Read', '2025-05-29 09:07:55'),
(133, 3, 1, 'Order Complete', 'Order Delivered & Payment Confirmed', 'Order #2 for POCO X6 Pro 5G has been successfully delivered to Aech Kirkstein by courier  . Payment has been confirmed and the order is now complete.', 'Read', '2025-05-29 09:07:55'),
(134, 2, 1, 'Order Complete', 'Order Delivered & Payment Confirmed', 'Your order #4 for Acer Aspire 7 Gaming Laptop (2024) has been successfully delivered and payment has been confirmed. Thank you for your purchase!', 'Read', '2025-05-29 09:07:57'),
(135, 3, 1, 'Order Complete', 'Order Delivered & Payment Confirmed', 'Order #4 for Acer Aspire 7 Gaming Laptop (2024) has been successfully delivered to Aech Kirkstein by courier  . Payment has been confirmed and the order is now complete.', 'Read', '2025-05-29 09:07:57'),
(136, 2, 1, 'Order Complete', 'Order Delivered & Payment Confirmed', 'Your order #5 for Xiaomi Redmi Note 13 5G has been successfully delivered and payment has been confirmed. Thank you for your purchase!', 'Read', '2025-05-29 09:07:58'),
(137, 3, 1, 'Order Complete', 'Order Delivered & Payment Confirmed', 'Order #5 for Xiaomi Redmi Note 13 5G has been successfully delivered to Aech Kirkstein by courier  . Payment has been confirmed and the order is now complete.', 'Read', '2025-05-29 09:07:58'),
(138, 2, 1, 'Order Complete', 'Order Delivered & Payment Confirmed', 'Your order #6 for Infinix Zero 30 4G has been successfully delivered and payment has been confirmed. Thank you for your purchase!', 'Read', '2025-05-29 09:08:00'),
(139, 3, 1, 'Order Complete', 'Order Delivered & Payment Confirmed', 'Order #6 for Infinix Zero 30 4G has been successfully delivered to Aech Kirkstein by courier  . Payment has been confirmed and the order is now complete.', 'Read', '2025-05-29 09:08:00'),
(140, 1, 3, 'Commission Received', 'New Commission from Seller', 'You have received ₱1599.92 commission from Order #2 (POCO X6 Pro 5G) by Aech Kirkstein', 'Unread', '2025-05-29 09:09:34'),
(141, 1, 4, 'Commission Received', 'New Commission from Courier', 'You have received ₱10.32 commission from Order #2 (POCO X6 Pro 5G) delivery by Aech Kirkstein', 'Unread', '2025-05-29 09:09:34'),
(142, 3, 1, 'Sales Added', 'Payment Received & Sales Updated', '₱18399.08 has been added to your sales from Order #2 (POCO X6 Pro 5G) by Aech Kirkstein. Commission: ₱1599.92', 'Read', '2025-05-29 09:09:34'),
(143, 4, 1, 'Sales Added', 'Delivery Payment Received & Sales Updated', '₱118.68 has been added to your sales from Order #2 (POCO X6 Pro 5G) delivery by Aech Kirkstein. Commission: ₱10.32', 'Unread', '2025-05-29 09:09:34'),
(144, 3, 1, 'Order Received', 'Order Received & Payment Confirmed', 'Aech Kirkstein has received Order #2 (POCO X6 Pro 5G). Payment has been confirmed and the order is now complete.', 'Read', '2025-05-29 09:09:34'),
(145, 1, 3, 'Commission Received', 'New Commission from Seller', 'You have received ₱3119.92 commission from Order #4 (Acer Aspire 7 Gaming Laptop (2024)) by Aech Kirkstein', 'Unread', '2025-05-29 09:09:39'),
(146, 1, 4, 'Commission Received', 'New Commission from Courier', 'You have received ₱6.32 commission from Order #4 (Acer Aspire 7 Gaming Laptop (2024)) delivery by Aech Kirkstein', 'Unread', '2025-05-29 09:09:39'),
(147, 3, 1, 'Sales Added', 'Payment Received & Sales Updated', '₱35879.08 has been added to your sales from Order #4 (Acer Aspire 7 Gaming Laptop (2024)) by Aech Kirkstein. Commission: ₱3119.92', 'Read', '2025-05-29 09:09:39'),
(148, 4, 1, 'Sales Added', 'Delivery Payment Received & Sales Updated', '₱72.68 has been added to your sales from Order #4 (Acer Aspire 7 Gaming Laptop (2024)) delivery by Aech Kirkstein. Commission: ₱6.32', 'Unread', '2025-05-29 09:09:39'),
(149, 3, 1, 'Order Received', 'Order Received & Payment Confirmed', 'Aech Kirkstein has received Order #4 (Acer Aspire 7 Gaming Laptop (2024)). Payment has been confirmed and the order is now complete.', 'Read', '2025-05-29 09:09:39'),
(150, 1, 3, 'Commission Received', 'New Commission from Seller', 'You have received ₱799.92 commission from Order #5 (Xiaomi Redmi Note 13 5G) by Aech Kirkstein', 'Unread', '2025-05-29 09:09:42'),
(151, 1, 4, 'Commission Received', 'New Commission from Courier', 'You have received ₱7.12 commission from Order #5 (Xiaomi Redmi Note 13 5G) delivery by Aech Kirkstein', 'Unread', '2025-05-29 09:09:42'),
(152, 3, 1, 'Sales Added', 'Payment Received & Sales Updated', '₱9199.08 has been added to your sales from Order #5 (Xiaomi Redmi Note 13 5G) by Aech Kirkstein. Commission: ₱799.92', 'Read', '2025-05-29 09:09:42'),
(153, 4, 1, 'Sales Added', 'Delivery Payment Received & Sales Updated', '₱81.88 has been added to your sales from Order #5 (Xiaomi Redmi Note 13 5G) delivery by Aech Kirkstein. Commission: ₱7.12', 'Unread', '2025-05-29 09:09:42'),
(154, 3, 1, 'Order Received', 'Order Received & Payment Confirmed', 'Aech Kirkstein has received Order #5 (Xiaomi Redmi Note 13 5G). Payment has been confirmed and the order is now complete.', 'Read', '2025-05-29 09:09:42'),
(155, 1, 3, 'Commission Received', 'New Commission from Seller', 'You have received ₱1519.84 commission from Order #6 (Infinix Zero 30 4G) by Aech Kirkstein', 'Unread', '2025-05-29 09:09:46'),
(156, 1, 4, 'Commission Received', 'New Commission from Courier', 'You have received ₱5.52 commission from Order #6 (Infinix Zero 30 4G) delivery by Aech Kirkstein', 'Unread', '2025-05-29 09:09:46'),
(157, 3, 1, 'Sales Added', 'Payment Received & Sales Updated', '₱17478.16 has been added to your sales from Order #6 (Infinix Zero 30 4G) by Aech Kirkstein. Commission: ₱1519.84', 'Read', '2025-05-29 09:09:46'),
(158, 4, 1, 'Sales Added', 'Delivery Payment Received & Sales Updated', '₱63.48 has been added to your sales from Order #6 (Infinix Zero 30 4G) delivery by Aech Kirkstein. Commission: ₱5.52', 'Unread', '2025-05-29 09:09:46'),
(159, 3, 1, 'Order Received', 'Order Received & Payment Confirmed', 'Aech Kirkstein has received Order #6 (Infinix Zero 30 4G). Payment has been confirmed and the order is now complete.', 'Read', '2025-05-29 09:09:46'),
(160, 1, 3, 'Commission Received', 'New Commission from Seller', 'You have received ₱999.92 commission from Order #1 (Vivo Y100) by Aech Kirkstein', 'Unread', '2025-05-29 09:09:48'),
(161, 1, 4, 'Commission Received', 'New Commission from Courier', 'You have received ₱6.32 commission from Order #1 (Vivo Y100) delivery by Aech Kirkstein', 'Unread', '2025-05-29 09:09:48'),
(162, 3, 1, 'Sales Added', 'Payment Received & Sales Updated', '₱11499.08 has been added to your sales from Order #1 (Vivo Y100) by Aech Kirkstein. Commission: ₱999.92', 'Read', '2025-05-29 09:09:48'),
(163, 4, 1, 'Sales Added', 'Delivery Payment Received & Sales Updated', '₱72.68 has been added to your sales from Order #1 (Vivo Y100) delivery by Aech Kirkstein. Commission: ₱6.32', 'Unread', '2025-05-29 09:09:48'),
(164, 3, 1, 'Order Received', 'Order Received & Payment Confirmed', 'Aech Kirkstein has received Order #1 (Vivo Y100). Payment has been confirmed and the order is now complete.', 'Read', '2025-05-29 09:09:48'),
(165, 3, 1, 'New Review', 'Customer Review Received', '  left a 4-star review (★★★★☆) for Order #2 (POCO X6 Pro 5G)', 'Read', '2025-05-29 09:09:53'),
(166, 3, 1, 'New Review', 'Customer Review Received', '  left a 4-star review (★★★★☆) for Order #5 (Xiaomi Redmi Note 13 5G): \"Good Product\"', 'Read', '2025-05-29 09:10:03'),
(167, 3, 1, 'New Review', 'Customer Review Received', '  left a 4-star review (★★★★☆) for Order #1 (Vivo Y100)', 'Read', '2025-05-29 09:10:14'),
(168, 3, 1, 'New Review', 'Customer Review Received', '  left a 3-star review (★★★☆☆) for Order #4 (Acer Aspire 7 Gaming Laptop (2024)): \"Good Product\"', 'Read', '2025-05-29 09:10:27'),
(169, 3, 1, 'New Review', 'Customer Review Received', '  left a 5-star review (★★★★★) for Order #6 (Infinix Zero 30 4G): \"Good Product\"', 'Read', '2025-05-29 09:10:35'),
(170, 2, 1, 'Order Confirmation', 'Order Placed Successfully', 'Your order has been placed successfully. Orders will be processed soon.', 'Read', '2025-05-29 09:13:58'),
(171, 3, 1, 'New Order', 'New Order Received - Aech Kirkstein', 'Aech Kirkstein has placed an order for: Intel Core i5 Pro Gaming Tower (Bundle Set). Please check your orders section to process the order.', 'Read', '2025-05-29 09:13:58'),
(172, 2, 1, 'Order Update', 'Order Approved', 'Your order for Intel Core i5 Pro Gaming Tower (Bundle Set) has been approved and is now being prepared for packing.', 'Read', '2025-05-29 09:14:21'),
(173, 2, 1, 'Order Update', 'Order Packed', 'Your order for Intel Core i5 Pro Gaming Tower (Bundle Set) has been packed and is ready for shipment.', 'Read', '2025-05-29 09:14:25'),
(174, 2, 1, 'Order Update', 'Order in Shipping', 'Your order for Intel Core i5 Pro Gaming Tower (Bundle Set) has been handed off to Standard Shipping and is now in shipping process.', 'Read', '2025-05-29 09:14:31'),
(175, 2, 1, 'Order Update', 'Order Shipped', 'Your order for Intel Core i5 Pro Gaming Tower (Bundle Set) has been shipped and is on its way to you.', 'Read', '2025-05-29 09:14:34'),
(176, 2, 1, 'Order Update', 'Courier Assigned', 'Your order #7 for Intel Core i5 Pro Gaming Tower (Bundle Set) has been assigned to courier Ace Maravilla and is awaiting acceptance for delivery.', 'Read', '2025-05-29 09:14:39'),
(177, 4, 1, 'Delivery Assignment', 'New Delivery Assignment - Order #7', 'You have been assigned to deliver Order #7 for Intel Core i5 Pro Gaming Tower (Bundle Set) to Aech Kirkstein. Please accept or decline this delivery assignment within 8 hours.', 'Unread', '2025-05-29 09:14:39'),
(178, 2, 1, 'Delivery Update', 'Order Out for Delivery', 'Great news! Your order #7 for Intel Core i5 Pro Gaming Tower (Bundle Set) is now out for delivery with courier  .', 'Read', '2025-05-29 09:14:52'),
(179, 3, 1, 'Delivery Update', 'Order Out for Delivery', 'Order #7 for Intel Core i5 Pro Gaming Tower (Bundle Set) has been accepted by courier   and is now out for delivery to Aech Kirkstein.', 'Read', '2025-05-29 09:14:52'),
(180, 2, 1, 'Order Complete', 'Order Delivered & Payment Confirmed', 'Your order #7 for Intel Core i5 Pro Gaming Tower (Bundle Set) has been successfully delivered and payment has been confirmed. Thank you for your purchase!', 'Read', '2025-05-29 09:15:46'),
(181, 3, 1, 'Order Complete', 'Order Delivered & Payment Confirmed', 'Order #7 for Intel Core i5 Pro Gaming Tower (Bundle Set) has been successfully delivered to Aech Kirkstein by courier  . Payment has been confirmed and the order is now complete.', 'Read', '2025-05-29 09:15:46'),
(182, 1, 3, 'Commission Received', 'New Commission from Seller', 'You have received ₱5200.00 commission from Order #7 (Intel Core i5 Pro Gaming Tower (Bundle Set)) by Aech Kirkstein', 'Unread', '2025-05-29 09:15:57'),
(183, 1, 4, 'Commission Received', 'New Commission from Courier', 'You have received ₱4.72 commission from Order #7 (Intel Core i5 Pro Gaming Tower (Bundle Set)) delivery by Aech Kirkstein', 'Unread', '2025-05-29 09:15:57'),
(184, 3, 1, 'Sales Added', 'Payment Received & Sales Updated', '₱59800.00 has been added to your sales from Order #7 (Intel Core i5 Pro Gaming Tower (Bundle Set)) by Aech Kirkstein. Commission: ₱5200.00', 'Read', '2025-05-29 09:15:57'),
(185, 4, 1, 'Sales Added', 'Delivery Payment Received & Sales Updated', '₱54.28 has been added to your sales from Order #7 (Intel Core i5 Pro Gaming Tower (Bundle Set)) delivery by Aech Kirkstein. Commission: ₱4.72', 'Unread', '2025-05-29 09:15:57'),
(186, 3, 1, 'Order Received', 'Order Received & Payment Confirmed', 'Aech Kirkstein has received Order #7 (Intel Core i5 Pro Gaming Tower (Bundle Set)). Payment has been confirmed and the order is now complete.', 'Read', '2025-05-29 09:15:57'),
(187, 3, 1, 'New Review', 'Customer Review Received', '  left a 5-star review (★★★★★) for Order #7 (Intel Core i5 Pro Gaming Tower (Bundle Set))', 'Read', '2025-05-29 09:16:01');

-- --------------------------------------------------------

--
-- Table structure for table `order_completed`
--

CREATE TABLE `order_completed` (
  `completed_id` int(11) NOT NULL,
  `order_id` int(11) NOT NULL,
  `date_completed` datetime NOT NULL DEFAULT current_timestamp(),
  `status` enum('Completed') NOT NULL DEFAULT 'Completed'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `order_completed`
--

INSERT INTO `order_completed` (`completed_id`, `order_id`, `date_completed`, `status`) VALUES
(1, 1, '2025-05-29 09:07:53', 'Completed'),
(2, 2, '2025-05-29 09:07:55', 'Completed'),
(3, 4, '2025-05-29 09:07:57', 'Completed'),
(4, 5, '2025-05-29 09:07:58', 'Completed'),
(5, 6, '2025-05-29 09:08:00', 'Completed'),
(6, 7, '2025-05-29 09:15:46', 'Completed');

-- --------------------------------------------------------

--
-- Table structure for table `order_delivery`
--

CREATE TABLE `order_delivery` (
  `delivery_id` int(11) NOT NULL,
  `order_id` int(11) NOT NULL,
  `courier_id` int(11) NOT NULL,
  `date_delivered` datetime NOT NULL DEFAULT current_timestamp(),
  `status` enum('For Delivery','Out for Delivery','Delivered') NOT NULL DEFAULT 'For Delivery'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `order_delivery`
--

INSERT INTO `order_delivery` (`delivery_id`, `order_id`, `courier_id`, `date_delivered`, `status`) VALUES
(1, 6, 4, '2025-05-29 09:07:21', 'Delivered'),
(2, 5, 4, '2025-05-29 09:07:24', 'Delivered'),
(3, 4, 4, '2025-05-29 09:07:27', 'Delivered'),
(4, 2, 4, '2025-05-29 09:07:32', 'Delivered'),
(5, 1, 4, '2025-05-29 09:07:34', 'Delivered'),
(6, 7, 4, '2025-05-29 09:14:39', 'Delivered');

-- --------------------------------------------------------

--
-- Table structure for table `order_packing`
--

CREATE TABLE `order_packing` (
  `packing_id` int(11) NOT NULL,
  `order_id` int(11) NOT NULL,
  `status` enum('Packing','Packed') NOT NULL DEFAULT 'Packing',
  `date_packed` datetime NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `order_packing`
--

INSERT INTO `order_packing` (`packing_id`, `order_id`, `status`, `date_packed`) VALUES
(1, 6, 'Packed', '2025-05-29 09:06:33'),
(2, 5, 'Packed', '2025-05-29 09:06:38'),
(3, 4, 'Packed', '2025-05-29 09:06:44'),
(4, 3, 'Packed', '2025-05-29 09:06:49'),
(5, 1, 'Packed', '2025-05-29 09:06:54'),
(6, 2, 'Packed', '2025-05-29 09:07:01'),
(7, 7, 'Packed', '2025-05-29 09:14:25');

-- --------------------------------------------------------

--
-- Table structure for table `order_received`
--

CREATE TABLE `order_received` (
  `received_id` int(11) NOT NULL,
  `order_id` int(11) NOT NULL,
  `buyer_id` int(11) NOT NULL,
  `date_received` datetime NOT NULL DEFAULT current_timestamp(),
  `status` enum('To Receive','Received') NOT NULL DEFAULT 'To Receive'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `order_received`
--

INSERT INTO `order_received` (`received_id`, `order_id`, `buyer_id`, `date_received`, `status`) VALUES
(1, 1, 2, '2025-05-29 09:07:53', 'Received'),
(2, 2, 2, '2025-05-29 09:07:55', 'Received'),
(3, 4, 2, '2025-05-29 09:07:57', 'Received'),
(4, 5, 2, '2025-05-29 09:07:58', 'Received'),
(5, 6, 2, '2025-05-29 09:08:00', 'Received'),
(6, 2, 2, '2025-05-29 09:09:34', 'Received'),
(7, 4, 2, '2025-05-29 09:09:39', 'Received'),
(8, 5, 2, '2025-05-29 09:09:42', 'Received'),
(9, 6, 2, '2025-05-29 09:09:46', 'Received'),
(10, 1, 2, '2025-05-29 09:09:48', 'Received'),
(11, 7, 2, '2025-05-29 09:15:46', 'Received'),
(12, 7, 2, '2025-05-29 09:15:57', 'Received');

-- --------------------------------------------------------

--
-- Table structure for table `order_shipping`
--

CREATE TABLE `order_shipping` (
  `shipping_id` int(11) NOT NULL,
  `order_id` int(11) NOT NULL,
  `logistic_name` varchar(50) NOT NULL,
  `date_shipping` datetime NOT NULL DEFAULT current_timestamp(),
  `date_shipped` datetime DEFAULT NULL,
  `status` enum('Shipping','Shipped') NOT NULL DEFAULT 'Shipping'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `order_shipping`
--

INSERT INTO `order_shipping` (`shipping_id`, `order_id`, `logistic_name`, `date_shipping`, `date_shipped`, `status`) VALUES
(1, 6, 'Standard Shipping', '2025-05-29 09:06:35', '2025-05-29 09:07:10', 'Shipped'),
(2, 5, 'Standard Shipping', '2025-05-29 09:06:40', '2025-05-29 09:07:12', 'Shipped'),
(3, 4, 'Standard Shipping', '2025-05-29 09:06:46', '2025-05-29 09:07:13', 'Shipped'),
(4, 1, 'Standard Shipping', '2025-05-29 09:06:57', '2025-05-29 09:07:16', 'Shipped'),
(5, 2, 'Standard Shipping', '2025-05-29 09:07:07', '2025-05-29 09:07:15', 'Shipped'),
(6, 7, 'Standard Shipping', '2025-05-29 09:14:31', '2025-05-29 09:14:34', 'Shipped');

-- --------------------------------------------------------

--
-- Table structure for table `product`
--

CREATE TABLE `product` (
  `product_id` int(11) NOT NULL,
  `product_info_id` int(11) NOT NULL,
  `variant` varchar(100) NOT NULL,
  `color` varchar(50) NOT NULL,
  `stock` int(11) NOT NULL CHECK (`stock` >= 0),
  `stock_status` enum('Active','Nearly Out of Stock','Out of Stock') DEFAULT NULL,
  `price` decimal(10,2) NOT NULL CHECK (`price` >= 0),
  `shipping_fee` decimal(10,2) NOT NULL,
  `status` enum('Active','Archived','Deleted') NOT NULL DEFAULT 'Active',
  `date_added` datetime NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `product`
--

INSERT INTO `product` (`product_id`, `product_info_id`, `variant`, `color`, `stock`, `stock_status`, `price`, `shipping_fee`, `status`, `date_added`) VALUES
(1, 1, '8GB RAM + 128GB Storage', 'Black', 20, 'Active', 18990.00, 70.00, 'Active', '2025-05-28 10:08:36'),
(2, 1, '8GB RAM + 128GB Storage', 'White', 20, 'Active', 18990.00, 70.00, 'Active', '2025-05-28 10:08:36'),
(3, 1, '8GB RAM + 128GB Storage', 'Lilac', 20, 'Active', 18990.00, 70.00, 'Active', '2025-05-28 10:08:36'),
(4, 2, '8GB RAM + 512GB SSD', 'Black', 19, 'Active', 38999.00, 79.00, 'Active', '2025-05-28 10:14:24'),
(5, 2, '16GB RAM + 1TB SSD', 'Black', 19, 'Active', 45999.00, 79.00, 'Active', '2025-05-28 10:14:24'),
(8, 4, 'Intel Core i5-12400F + GTX 1660 Super', 'Matte Black Case (with RGB fans)', 18, 'Active', 32500.00, 59.00, 'Active', '2025-05-28 10:27:24'),
(9, 4, 'Intel Core i5-12400F + RTX 3060', 'Matte Black Case (with tempered glass)', 20, 'Active', 42999.00, 59.00, 'Active', '2025-05-28 10:27:24'),
(10, 5, 'Variant 1:', 'Sky Blue', 20, 'Active', 3599.00, 79.00, 'Active', '2025-05-28 10:35:54'),
(11, 5, 'Variant 1:', 'Midnight Black', 20, 'Active', 3599.00, 79.00, 'Active', '2025-05-28 10:35:54'),
(12, 6, '6GB + 128GB', 'Graphite Black', 20, 'Active', 9999.00, 89.00, 'Active', '2025-05-28 10:42:12'),
(13, 6, '6GB + 128GB', 'Ocean Teal', 19, 'Active', 9999.00, 89.00, 'Active', '2025-05-28 10:42:12'),
(14, 6, '6GB + 128GB', 'Arctic White', 20, 'Active', 9999.00, 89.00, 'Active', '2025-05-28 10:42:12'),
(15, 7, '8GB + 256GB', 'Sunset Gold', 18, 'Active', 9499.00, 69.00, 'Active', '2025-05-28 10:46:42'),
(16, 7, '8GB + 256GB', 'Rome Green', 20, 'Active', 9499.00, 69.00, 'Active', '2025-05-28 10:46:42'),
(17, 8, '8GB RAM + 256GB', 'Crystal Black', 20, 'Active', 12499.00, 69.00, 'Active', '2025-05-28 11:01:42'),
(18, 8, '8GB RAM + 256GB', 'Breeze Green', 20, 'Active', 12499.00, 69.00, 'Active', '2025-05-28 11:01:42'),
(19, 9, '8GB RAM + 512GB Storage', 'Glamorous Green', 20, 'Active', 12999.00, 79.00, 'Active', '2025-05-28 11:05:30'),
(20, 9, '8GB RAM + 512GB Storage', 'Titanium Silver', 20, 'Active', 12999.00, 79.00, 'Active', '2025-05-28 11:05:30'),
(21, 9, '8GB RAM + 512GB Storage', 'Midnight Black', 20, 'Active', 12999.00, 79.00, 'Active', '2025-05-28 11:05:30'),
(22, 10, '2GB RAM + 512GB', 'Yellow', 19, 'Active', 19999.00, 129.00, 'Active', '2025-05-28 11:08:19'),
(23, 10, '2GB RAM + 512GB', 'Phantom Black', 20, 'Active', 19999.00, 129.00, 'Active', '2025-05-28 11:08:19'),
(24, 10, '2GB RAM + 512GB', 'Grey', 20, 'Active', 19999.00, 129.00, 'Active', '2025-05-28 11:08:19'),
(25, 11, '8GB RAM + 256GB', 'Crystal Black', 19, 'Active', 12499.00, 79.00, 'Active', '2025-05-28 11:11:31'),
(26, 11, '8GB RAM + 256GB', 'Breeze Green', 20, 'Active', 12499.00, 79.00, 'Active', '2025-05-28 11:11:31'),
(27, 12, 'AMD Ryzen 5 7520U, 8GB RAM, 512GB SSD', 'Jet Black', 20, 'Active', 25490.00, 79.00, 'Active', '2025-05-28 11:29:08'),
(28, 12, 'AMD Ryzen 5 7520U, 8GB RAM, 512GB SSD', 'Silver', 20, 'Active', 25490.00, 79.00, 'Active', '2025-05-28 11:29:08'),
(29, 12, 'AMD Ryzen 5 7520U, 12GB RAM, 512GB SSD', 'Jet Black', 20, 'Active', 27490.00, 79.00, 'Active', '2025-05-28 11:29:08'),
(30, 12, 'AMD Ryzen 5 7520U, 12GB RAM, 512GB SSD', 'Silver', 20, 'Active', 27490.00, 79.00, 'Active', '2025-05-28 11:29:08'),
(31, 13, 'Intel Core i3-1315U, 8GB RAM, 256GB SSD', 'Abyss Blue', 20, 'Active', 27990.00, 79.00, 'Active', '2025-05-28 11:37:12'),
(32, 13, 'Intel Core i3-1315U, 8GB RAM, 256GB SSD', 'Arctic Grey', 20, 'Active', 27990.00, 79.00, 'Active', '2025-05-28 11:37:12'),
(33, 14, 'Intel i5-1235U, 8GB RAM, 512GB SSD', 'Classic Black', 20, 'Active', 32999.00, 79.00, 'Active', '2025-05-28 11:42:48'),
(34, 14, 'Intel i5-1235U, 8GB RAM, 512GB SSD', 'Urban Silver', 20, 'Active', 32999.00, 79.00, 'Active', '2025-05-28 11:42:48'),
(35, 15, 'M1 Chip, 8GB RAM, 256GB SSD', 'Space Gray', 20, 'Active', 49990.00, 79.00, 'Active', '2025-05-28 11:49:27'),
(36, 15, 'M1 Chip, 8GB RAM, 256GB SSD', 'Silver', 20, 'Active', 49990.00, 79.00, 'Active', '2025-05-28 11:49:27'),
(37, 15, 'M1 Chip, 8GB RAM, 256GB SSD', 'Gold', 20, 'Active', 49990.00, 79.00, 'Active', '2025-05-28 11:49:27'),
(38, 16, 'Intel i5-1240P, 16GB RAM, 512GB SSD', 'Space Gray', 20, 'Active', 34999.00, 79.00, 'Active', '2025-05-28 11:52:18'),
(39, 17, 'Intel Core i5-1335U, 16GB RAM, 512GB SSD', 'Platinum Silver', 20, 'Active', 42999.00, 79.00, 'Active', '2025-05-28 11:56:41'),
(40, 17, 'Intel Core i5-1335U, 16GB RAM, 512GB SSD', 'Pebble Green', 20, 'Active', 42999.00, 79.00, 'Active', '2025-05-28 11:56:41'),
(41, 18, 'Intel Core i5-12500H, 16GB RAM, 512GB SSD, RTX 4060', 'Black', 20, 'Active', 59895.00, 79.00, 'Active', '2025-05-28 12:00:03'),
(42, 19, 'Intel Core i5-12400, 8GB RAM, 512GB SSD', 'Iron Gray', 20, 'Active', 33499.00, 129.00, 'Active', '2025-05-28 12:05:30'),
(43, 20, 'Intel Core i3-13100, 8GB RAM, 1TB HDD', 'Carbon Black', 62, 'Active', 27990.00, 129.00, 'Active', '2025-05-28 12:09:13'),
(44, 21, 'AMD Ryzen 5 5600G, 8GB RAM, 512GB SSD', 'Natural Silver', 52, 'Active', 31499.00, 129.00, 'Active', '2025-05-28 12:12:06'),
(45, 22, 'AMD Ryzen 3 5300G, 8GB RAM, 256GB SSD + 1TB HDD', 'Cloud Grey', 84, 'Active', 26990.00, 129.00, 'Active', '2025-05-28 12:15:01'),
(46, 23, 'Intel i5-12400, 8GB RAM, 512GB SSD', 'Matte Black', 52, 'Active', 29499.00, 129.00, 'Active', '2025-05-28 12:17:13'),
(47, 24, 'Intel N5105, 8GB RAM, 256GB SSD', 'Black', 92, 'Active', 19999.00, 129.00, 'Active', '2025-05-28 12:19:08'),
(48, 25, 'Ryzen 5 4600G, 16GB RAM, 512GB SSD', 'Black', 24, 'Active', 23990.00, 129.00, 'Active', '2025-05-28 12:25:01'),
(49, 26, 'Intel i7-12700, 16GB RAM, 1TB SSD', 'Jet Black', 61, 'Active', 49999.00, 129.00, 'Active', '2025-05-28 12:28:54'),
(50, 26, 'Intel i5-12700, 16GB RAM, 1TB SSD', 'Silver', 52, 'Active', 46999.00, 129.00, 'Active', '2025-05-28 12:31:05'),
(51, 27, 'Wired 3.5mm Gaming Headset', 'Black', 52, 'Active', 1999.00, 79.00, 'Active', '2025-05-28 12:52:58'),
(52, 27, 'Wired 3.5mm Gaming Headset', 'White', 42, 'Active', 2099.00, 79.00, 'Active', '2025-05-28 12:52:58'),
(53, 28, 'Bluetooth On-Ear Headphones', 'Blue', 62, 'Active', 2799.00, 79.00, 'Active', '2025-05-28 12:56:18'),
(54, 28, 'Bluetooth On-Ear Headphones', 'Beige', 21, 'Active', 2799.00, 79.00, 'Active', '2025-05-28 12:56:18'),
(55, 28, 'Bluetooth On-Ear Headphones', 'Black', 92, 'Active', 2699.00, 79.00, 'Active', '2025-05-28 12:56:18'),
(56, 29, 'Portable Bluetooth Speaker', 'Black & Brass', 92, 'Active', 8990.00, 79.00, 'Active', '2025-05-28 13:02:05'),
(57, 29, 'Portable Bluetooth Speaker', 'Cream', 52, 'Active', 9200.00, 79.00, 'Active', '2025-05-28 13:02:05'),
(58, 30, 'USB Condenser Microphone Kit', 'Black', 85, 'Active', 3199.00, 79.00, 'Active', '2025-05-28 13:05:25'),
(59, 31, 'Wired Open-Back Headphones', 'Black', 52, 'Active', 12799.00, 79.00, 'Active', '2025-05-28 13:08:23'),
(60, 32, 'Bluetooth/Optical Bookshelf Speakers', 'Walnut', 52, 'Active', 5999.00, 79.00, 'Active', '2025-05-28 13:18:01'),
(61, 32, 'Bluetooth/Optical Bookshelf Speakers', 'Black', 52, 'Active', 5899.00, 79.00, 'Active', '2025-05-28 13:18:01'),
(62, 33, 'Wireless/Bluetooth Headset', 'Black & Neon Yellow', 85, 'Active', 3599.00, 79.00, 'Active', '2025-05-28 13:22:13'),
(63, 33, 'Wireless/Bluetooth Headset', 'White & Lilac', 85, 'Active', 3699.00, 79.00, 'Active', '2025-05-28 13:22:13'),
(64, 34, 'Hybrid XLR/USB-C Microphone', 'Black', 25, 'Active', 15999.00, 79.00, 'Active', '2025-05-28 13:26:05'),
(65, 34, 'Hybrid XLR/USB-C Microphone', 'Silver', 25, 'Active', 16499.00, 79.00, 'Active', '2025-05-28 13:26:05'),
(66, 35, 'USB Webcam', 'Black', 20, 'Active', 3999.00, 69.00, 'Active', '2025-05-28 13:36:53'),
(67, 36, 'Vlog Camera Kit', 'Black', 20, 'Active', 28499.00, 129.00, 'Active', '2025-05-28 13:39:47'),
(68, 36, 'Vlog Camera Kit', 'White', 20, 'Active', 28799.00, 129.00, 'Active', '2025-05-28 13:39:47'),
(69, 37, 'Action Camera', 'Black', 20, 'Active', 26990.00, 69.00, 'Active', '2025-05-28 13:42:36'),
(70, 38, 'Mirrorless Kit (15-45mm lens)', 'Black', 20, 'Active', 33999.00, 79.00, 'Active', '2025-05-28 13:44:52'),
(71, 38, 'Mirrorless Kit (15-45mm lens)', 'White', 20, 'Active', 34299.00, 79.00, 'Active', '2025-05-28 13:44:52'),
(72, 39, '360° Camera', 'Black', 20, 'Active', 27500.00, 69.00, 'Active', '2025-05-28 13:48:24'),
(73, 40, 'HDMI-to-USB Video Capture', 'Black', 20, 'Active', 6799.00, 89.00, 'Active', '2025-05-28 13:50:21'),
(74, 41, 'Creator Combo Kit', 'Black', 20, 'Active', 22990.00, 129.00, 'Active', '2025-05-28 13:52:48'),
(75, 42, '4K USB Webcam', 'Black', 20, 'Active', 7999.00, 59.00, 'Active', '2025-05-28 13:54:55'),
(76, 43, '7-inch Smart Display', 'Charcoal', 20, 'Active', 4899.00, 79.00, 'Active', '2025-05-28 14:02:26'),
(77, 43, '7-inch Smart Display', 'Chalk', 20, 'Active', 4899.00, 79.00, 'Active', '2025-05-28 14:02:26'),
(78, 44, 'Smart Door Lock', 'Matte Black', 20, 'Active', 11999.00, 109.00, 'Active', '2025-05-28 14:04:36'),
(79, 45, 'Smart Speaker', 'Deep Sea Blue', 20, 'Active', 2799.00, 39.00, 'Active', '2025-05-28 14:06:52'),
(80, 45, 'Smart Speaker', 'Glacier White', 20, 'Active', 2799.00, 39.00, 'Active', '2025-05-28 14:06:52'),
(81, 45, 'Smart Speaker', 'Charcoal', 20, 'Active', 2799.00, 39.00, 'Active', '2025-05-28 14:06:52'),
(82, 46, 'Smart Thermo-Hygrometer', 'White', 20, 'Active', 699.00, 29.00, 'Active', '2025-05-28 14:08:20'),
(83, 47, 'Zigbee Motion Sensor', 'White', 20, 'Active', 1499.00, 69.00, 'Active', '2025-05-28 14:09:53'),
(84, 48, 'Smart IR/RF Controller', 'Black', 20, 'Active', 1899.00, 59.00, 'Active', '2025-05-28 14:12:52'),
(85, 49, 'Smart LED Bulb', 'White', 20, 'Active', 1599.00, 69.00, 'Active', '2025-05-28 14:15:15'),
(86, 49, 'Smart LED Bulb', 'White + Color', 20, 'Active', 2199.00, 69.00, 'Active', '2025-05-28 14:15:15'),
(87, 50, 'Indoor Wi-Fi Camera', 'White', 20, 'Active', 1499.00, 39.00, 'Active', '2025-05-28 14:17:23'),
(88, 51, 'Body Only', 'Black', 52, 'Active', 48999.00, 79.00, 'Active', '2025-05-28 14:33:14'),
(89, 51, 'w/ RF-S 18–45mm Lens Kit', 'Black', 52, 'Active', 56999.00, 79.00, 'Active', '2025-05-28 14:33:14'),
(90, 52, '16–50mm Kit', 'Black', 52, 'Active', 45490.00, 79.00, 'Active', '2025-05-28 14:35:51'),
(91, 53, 'Body Only', 'Silver', 52, 'Active', 42899.00, 79.00, 'Active', '2025-05-28 14:39:34'),
(92, 53, '15–45mm Lens Kit', 'Black', 52, 'Active', 42899.00, 79.00, 'Active', '2025-05-28 14:39:34');

-- --------------------------------------------------------

--
-- Table structure for table `product_feedback`
--

CREATE TABLE `product_feedback` (
  `feedback_id` int(11) NOT NULL,
  `shop_id` int(11) NOT NULL,
  `product_id` int(11) NOT NULL,
  `sender_id` int(11) NOT NULL,
  `feedback` text NOT NULL,
  `date_feedback` datetime NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `product_feedback`
--

INSERT INTO `product_feedback` (`feedback_id`, `shop_id`, `product_id`, `sender_id`, `feedback`, `date_feedback`) VALUES
(1, 1, 13, 2, 'Good Product', '2025-05-29 09:10:03'),
(2, 1, 4, 2, 'Good Product', '2025-05-29 09:10:27'),
(3, 1, 15, 2, 'Good Product', '2025-05-29 09:10:35');

-- --------------------------------------------------------

--
-- Table structure for table `product_images`
--

CREATE TABLE `product_images` (
  `images_id` int(11) NOT NULL,
  `product_info_id` int(11) NOT NULL,
  `product_image` varchar(299) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `product_images`
--

INSERT INTO `product_images` (`images_id`, `product_info_id`, `product_image`) VALUES
(1, 1, 'lrwQClXvWuP1qA__ucsafw_download_5.jpg'),
(2, 1, 'rUm_r3faWDX5VmeAYaCxSQ_download_4.jpg'),
(3, 1, 'r32gfk4hBN9GBoVUKlZ9Pg_download_3.jpg'),
(4, 2, 'WSnpGzr67O_jm9r_Qyt7sQ_images_12.jpg'),
(5, 2, 'ynZY9TKw09FTIDniuvns0w_images_11.jpg'),
(6, 2, 'yEQtvPrtRJfLwcuYpQ5fyw_download_7.jpg'),
(7, 4, '7CM8mjDdfEiAT1K2ezmCXQ_ph-11134207-7rasd-m7622mjarocrec.jpg'),
(8, 4, 'OHUQGqJKtzFAcLURkrlL4Q_images_13.jpg'),
(9, 5, 'vQVDBtoko3TY_Z2FSwOEUQ_realme-note-50-review.jpg'),
(10, 5, 'EJfdhN8pLa4PdE14vHsNtw_download_8.jpg'),
(11, 5, '94iZlXD6CA2OcsPvqeBHzA_BLUE-1.png'),
(12, 6, 'mV0PUn7I4cM95JTYeY-pCg_m-note13-tel-green.png'),
(13, 6, 'otC6-gbXrIdQ3aOLJHB4BA_images_15.jpg'),
(14, 6, '6sxmV4mKVRJzodY5PCLNXg_CYBERZONE-WEBSITE-UPLOAD-1080--1080-px-16-2.png'),
(15, 7, '_ApTE-k1d1zz1MRcACz3lw_Infinix-Zero-30-4G-price-and-specs-via-Revu-Philippines-881x461.jpg'),
(16, 7, 'DjCbVAYPtnAKiolxYZhOMQ_ZERO-30-4G_2.jpg'),
(17, 7, 'ihr0h7A9y6-vFPBjHeDbcg_GREENTELCOM.PH-2024-02-15T095651.088.png'),
(18, 8, 'D5pnjYDtATpwo6o1ramPTg_240107-GadgetMatch-TECNO-SPARK-20-Pro-Beauty-Back-3.jpg'),
(19, 8, 'XNU59BeXwjmMcknBoX0EfA_240107-GadgetMatch-TECNO-SPARK-20-Pro-Beauty-108MP-Camera-3.jpg'),
(20, 8, '9TbLToLBGDUAxugHIl6KSw_images_16.jpg'),
(21, 8, 'E9xTbmootcQUvxUYZOt7pA_240107-GadgetMatch-TECNO-SPARK-20-Pro-Beauty-Back-3_-_Copy.jpg'),
(22, 9, 'TfPGfAqvoRAI-pYx-hf3Qw_images_19.jpg'),
(23, 9, 'yj38uHX_CzJGCBoaKPShWQ_images_18.jpg'),
(24, 9, 'm4C1nM86wTKletRKN5qOkg_images_17.jpg'),
(25, 10, '6Cy73Ev1YTYlAoVlWzNa0w_fb199e5433ffcbcc38eeff0042fe0fbe.jpg'),
(26, 10, 't_LNj9ixJmo8FxWtEj_uWQ_download_9.jpg'),
(27, 10, 'JinG_YgiMz2NXryFEmJZEw_31856e113e6de73a9e91d1e359640d8e.jpg'),
(28, 11, 'JXv7he1O87gYddWTKAD3xQ_images_21.jpg'),
(29, 11, 'UdD_FVU57P-rUeIQ4smFyA_images_20.jpg'),
(30, 11, 'uCZmf4H68XPopv2ebEi1Ew_57.jpg'),
(31, 12, 'gNhZ470GL87RA_T8yYO1uA_71H53Sqsr2L.jpg'),
(32, 12, '_OQKm_fawP_lTuZtFgQbsg_81EWtB70npL._AC_SL1500_.jpg'),
(33, 12, 'mTh09CqcSrhRUxAfTnyPTA_images_22.jpg'),
(34, 12, 'ceMOWz7I9eKV7bEbnSLyXg_Acer-Aspire-3-Slim-A314-22-R430-1-1.jpg'),
(35, 12, 'Y3QshsyEDQ2bljs4wLyknw_61qyr1kbhcS._AC_SL1280_-medium.jpg'),
(36, 12, 'wj2OCwiFU2Hc3q7xnvXGlA_51zKuGBRSL.jpg'),
(37, 13, '1UqrqEAY_OZBLbcvTaFYxg_images_23.jpg'),
(38, 13, 'GWyouhkv6fGdABWfO8Fgnw_Screenshot_2025-05-28_113140.png'),
(39, 13, 'q7clUkTATDE1Odo8haXXzw_Screenshot_2025-05-28_113109.png'),
(40, 13, 'xxoeU0Eb6DQ4nQUqdte0Ag_download_10.jpg'),
(41, 13, 'znrJ9s4qKlOmMwaV-_WtZg_Lenovo-Ideapad-Slim-3-151AU7-82RK00WKPH-min.jpg'),
(42, 14, 'b8EPfRTNlAY4m8wluqE_LA_600.png'),
(43, 14, 'hrhKsg8-hT7dRh656lVy9g_prod-phtoto-3c.png'),
(44, 14, 'M6nVXOVu_jsDvn-NOmB82A_prod-phtoto-2c.png'),
(45, 14, 'prFFZRlbv_GhWnmnl5BUnw_id-modern14.png'),
(46, 14, '5Nhk1cUmwWyX07QBjMONCg_1024.png'),
(47, 15, 'OvT9FbOk6OIPRx0k7RbJUQ_ph-11134201-7rasl-m6qk62gk7uh754.jpg'),
(48, 15, '3-bHOYpyve6ZizXpTxTUkw_Screenshot_2025-05-28_114711.png'),
(49, 15, 'gROYI6TpKv9dFo6VUXQ5Cg_Screenshot_2025-05-28_114652.png'),
(50, 15, 'tBVYkmv3Ut9neSEXCv0fYg_Screenshot_2025-05-28_114632.png'),
(51, 15, 'vQOYlOqkZOtgeeWrWAyaWw_Screenshot_2025-05-28_114613.png'),
(52, 16, 'OR8ysDrNYBP_b4jfNBuuHQ_huawei-matebook-d-14-2023-screen.png'),
(53, 16, 'MoY4Bv6Vd_dh4qduEi0KPw_GREENTELCOM.PH-2024-02-20T105825.319.png'),
(54, 16, 'YPY6rQ2lZUkPGO_nE169QQ_images_25.jpg'),
(55, 16, 'ymwNIj438JBcECarNp6VcA_huawei-matebook-d-14-2023-memory-1.png'),
(56, 16, '1eekcaWeKxomloQy6lekrA_huawei-matebook-d-14-2023-design.jpg'),
(57, 17, '6wLLgz-EZVLwCGEkq4b2Dw_images_26.jpg'),
(58, 17, 'H5iS7yF-YzBtnce4oSXrOw_download_14.jpg'),
(59, 17, 'OO8orOPNc6_eaLCy0dKm1Q_download_13.jpg'),
(60, 17, '4LsOVyXF4wrYSa6m7O4_nw_download_12.jpg'),
(61, 17, '2ZssOx2CrgOGbyogMwLY_A_download_11.jpg'),
(62, 17, 'u_ZWUIcASaA86Cl-4xDnjg_Laptop-Dell-Inspiron-14-5430-i5-1340P-3.jpg'),
(63, 18, 'ncF-p5WQjWqhaHZJtceFnA_71tgmKoXApL.jpg'),
(64, 18, 'aRauQHvMUJtdDtuLrwsa_w_Screenshot_2025-05-28_115810.png'),
(65, 18, 'CQxBN-jzh0F4oMLvBYyFbQ_Png_1.png'),
(66, 18, '-o043IaMnenu8iOJGHNpwQ_Screenshot_2025-05-28_115750.png'),
(67, 18, 'd1ycVnIDRfXIlUMEDsz26g_Png.png'),
(68, 19, '0MNPV3TvboK5bbxhFVDd7Q_Screenshot_2025-05-28_120242.png'),
(69, 19, '1wCzs_rJot460EUfuJ0JKA_Screenshot_2025-05-28_120227.png'),
(70, 19, 'itu_T-jHZQE0-CS6ZHS0ew_download_15.jpg'),
(71, 20, 'tRGGVFGgnr3byTEu5Sp1lQ_images_28.jpg'),
(72, 20, 'BCZC619QlO_p6u_2uGUuVA_sddefault.jpg'),
(73, 20, 'wBgZxsVQN3JucnH4mfA1xw_Screenshot_2025-05-28_120724.png'),
(74, 20, 'TGnlE_tK9VZQacY9aGW5yQ_Screenshot_2025-05-28_120704.png'),
(75, 21, 'NNH_rrldMZitKHHXL3ixkw_images_30.jpg'),
(76, 21, '_0sTxKVIQvg31_xRh3OZzw_download_16.jpg'),
(77, 21, 'sFUoRaXJPWFtJfKByL4N5g_HP-Pavilion-TP01-3117c-Desktop.jpg'),
(78, 22, 'j3o0XQiyuUzEbGRcS-pkVw_ph-11134207-7r98x-lv3zp7nh41zm66.jpg'),
(79, 22, '_FA6q5KRj8NiyrwSI7FeNQ_download_17.jpg'),
(80, 22, 'fJC8VlCbo4dpALeaTTBTPA_Screenshot_2025-05-28_121309.png'),
(81, 23, 'G1IDWvjufTEjmy7zVm1org_600_1.png'),
(82, 23, 'hCNNiN3LgptjhsNwcai1iA_download_18.jpg'),
(83, 23, 'Ak4krXal5Ot_JvTXHZlCeA_83-151-279-15.jpg'),
(84, 23, 'zKreCckqHyl8mjFJRKc3VA_msi-pro-dp21-io.png'),
(85, 23, '88dxiWflS5JMsrpWnyTyoQ_msi-pro-dp21-maintain-02.png'),
(86, 24, '0PHqgdggw0qhQsD8dnMRTw_download_21.jpg'),
(87, 24, '0MmFWgzngaf_i-9SUiXzOw_download_20.jpg'),
(88, 24, 'B_VO_JjEMKrnPaFKLm4pPQ_download_19.jpg'),
(89, 25, '9yMH9utr-k3K-xP2pYgODg_opAYYoeNKNpFR87QaVDe3R.jpg'),
(90, 25, 'ygt7R6B-zCpWp1jf8y4BHw_3200G.jpg'),
(91, 25, 'd0e3uc6FjhoMe18Uor6biQ_b2W4pMBWM2Rjrf49S2vzRB.jpg'),
(97, 26, 'o-b95IbP01wZoM6AYTLmwA_61unYK0kPmL._AC_UF350350_QL80_.jpg'),
(98, 26, 'au5tXnVE9ZfM7tvPcsxFEg_images_31.jpg'),
(99, 26, 'iMwwVcxwR1IcDrrXdN4-_Q_Screenshot_2025-05-28_122650.png'),
(100, 26, 'fTC3uXBR0nbPVE8AV7bDDw_a21-i714th_2166_detail.jpg'),
(101, 26, 'e4b8k8mDVaWUo7wosgxPMQ_Screenshot_2025-05-28_122627.png'),
(102, 27, 'j0ft7YjgmGRclP4FaJw2XQ_JBL_Quantum_100_Box_Image_Black_Side.png'),
(103, 27, 'S2ZxkH0_YJexq96UMaJDbQ_171641_2022.jpg'),
(104, 27, 'rIasOvBuNzPV5-GlsnYM1g_Screenshot_2025-05-28_125103.png'),
(105, 27, 'zf6TIVj3YGgjj9tkb0O35Q_Screenshot_2025-05-28_125049.png'),
(106, 27, 'AnmjVtvv-swrdNEJOgWeOA_Screenshot_2025-05-28_125033.png'),
(107, 28, '2LIyTgNWLo-qzkBstHNzIg_cn-11134207-7qukw-lgq1d4pyqu709b_1.jpg'),
(108, 28, 'VynB-d6SAl8zSiirHOuonw_images_33.jpg'),
(109, 28, 'q_M-N5o6pKua3ms4E7qJ6Q_images_32.jpg'),
(110, 28, 'Xrn3vfNYHtY_Aa9XDGkNOQ_download_24.jpg'),
(111, 29, 'SeD2K_i9Hh7N_rcJUYKzVQ_Marshall-Emberton-II-black-11-900x900.jpg'),
(112, 29, 'DgUqynE-qMsAOikOxJO_CQ_Screenshot_2025-05-28_125926.png'),
(113, 29, 'IE3x_SRnCBL8tvjqqCtWqg_Screenshot_2025-05-28_125913.png'),
(114, 29, '4L3-J_qlXDeha73lb1huPQ_PbJoVMfEU3HWEECV9vVEsh_watermark_400.jpg'),
(115, 29, 'wEoxsxJ15pGuO0qLc_k-ZQ_Screenshot_2025-05-28_125807.png'),
(116, 29, 'g1xQOUE__L5URKyNt_hvaw_ph-11134207-7rasc-m6qihnoesadxbd.jpg'),
(117, 29, 'CxDQjy2w63Y3NDgOTRar8g_Screenshot_2025-05-28_125741.png'),
(118, 30, 'JU7z3hsYkT3OZLLGBd0cxQ_715J35elo5L._AC_SL1500_.jpg'),
(119, 30, 'dCSPrMdpVjLRlqTqXUzKjA_61JnQYX-6xL.jpg'),
(120, 30, 'M-heZvHO2aWenjnR_faGRA_0645804073203fc8495a278da3852f57.jpg'),
(121, 31, 'GvxpElDuj4u0Yvn0mFoZTg_SEN-509144-4.jpg'),
(122, 31, 'WVoMdPhUOP4E4TCd_e20Yw_Screenshot_2025-05-28_130618.png'),
(123, 31, '97nMxPbxFgxrRERg2roWJA_HD_560S_e-commerce_ATF_01.jpg'),
(124, 32, 'LMll1PDL5vD1Q0ydP3madg_images_36.jpg'),
(125, 32, 'KmhnCGY9VeKuoOJo12Iwfw_images_35.jpg'),
(126, 32, '577GZixS6S3rmVCvO4-l0w_images_34.jpg'),
(127, 32, 'Cdmhtd2jcu230fBSbGeSrw_R1280DB-BLACK-1.jpg'),
(128, 33, 'QVIcery0ZMBzWUFWJLqUCA_download_29.jpg'),
(129, 33, '4cLMgUSgK_WBMzLYXCD_qg_download_28.jpg'),
(130, 33, 'GQDfyUz31UOWScZanwn_Ow_download_27.jpg'),
(131, 33, 'kS6uq68a54ELXf03902lEw_download_26.jpg'),
(132, 34, '_43QzOGl2p6vqU0Vdli-bA_Screenshot_2025-05-28_132346.png'),
(133, 34, 'ooA7AxJEUd4sGs13H_WHgg_Screenshot_2025-05-28_132332.png'),
(134, 34, 'kB_GFVCpM7GK6yWfghQo0A_Screenshot_2025-05-28_132318.png'),
(135, 35, '_tqgY_-PW4A6YHAj5lVidQ_images_37.jpg'),
(136, 35, 'GvOPxKjyQaybSmz9hC8j3w_GmxhF6gPGczGwNjf2ztT4e.jpg'),
(137, 35, 'O29C28Xd4lR3KlTFFiEKRw_download_31.jpg'),
(138, 36, 'R3ZSd_V_1OrEtPY0FDXrqw_images_38.jpg'),
(139, 36, 'b3P40UkP7quj3SqIsao9Ig_185832_2022_2.jpg'),
(140, 36, 'HT2sbuA7R7GuMjkYA0uEtQ_ph-11134207-7r98o-lxa23rnb8bj5c4.jpg'),
(141, 37, 'OS4cGwZtou5yFI4Modar0A_Hero11mini-9g.jpg'),
(142, 37, 'C1mBOuegYelOQz0Qsu5_xA_images_41.jpg'),
(143, 37, 'vX4F3qlglEpe_VTWxuvERw_images_40.jpg'),
(144, 38, 'tE8BORpUhqSGX8KDsA5I4A_canon-eos-m50-mark-ii-ef-m-18-150mm-f35-63-is-stm-161415869583560304.jpg'),
(145, 38, 'I9VbnbbisQcLlQRj8OG4Lw_images_42.jpg'),
(146, 38, '0Hq1VJgmDOB_G2plLO1jkg_d44fb276598309fdceab3ee9a8ad4a16.jpg'),
(147, 39, 'buSBWkbbew8yXYoSO5Eqxg_images_46.jpg'),
(148, 39, 'ocJKkrNItVuxoc3in-Mbiw_images_45.jpg'),
(149, 39, 'jK9En-MwuWRSw8OzcN9Vow_images_44.jpg'),
(150, 40, '_BaZALNAPhT6e-ndF9Rh9w_51mRg8baEL._AC_UF8941000_QL80_.jpg'),
(151, 40, 'ff4aLX4PXi14ivnZbLUxUg_images_47.jpg'),
(152, 40, 'HDMHIZu25YiSrOK4L5CZfw_cam-link-4k-01_w8qj1h.jpg'),
(153, 41, 'Be2HS_F0oOD_hOI3cVhQyw_41EskCYxfVL._AC_UF8941000_QL80_.jpg'),
(154, 41, '1E7wKBaZrT3lHRgh0WCw1g_images_48.jpg'),
(155, 41, 'C8F-bze6pCUIksYv9GIDhQ_download_33.jpg'),
(156, 42, 'qbFt8YPEXAil2Eeg-UZjAQ_51iNoWvCo4L._AC_UF8941000_QL80_.jpg'),
(157, 42, 'zNz-Cfx_ZLJnsSu2wlputg_images_49.jpg'),
(158, 42, 'oB98xHXmZyJ8dlkP95cUWA_61RuzGIUVL._AC_UF8941000_QL80_.jpg'),
(159, 43, 'MmMwI5quhwOiQjr1pIlzXw_images_54.jpg'),
(160, 43, 'RL1wH0bUIGybKR6CHjzYxw_images_53.jpg'),
(161, 43, '-YVIAsvJAPGOaa1NvSOtjw_images_51.jpg'),
(162, 43, 'F7f1hG6128Gy_V80bo3vEw_images_50.jpg'),
(163, 44, '0bGODRf90-3NZ7_oxWArqg_images_56.jpg'),
(164, 44, '7VyzHJWzcUItSyHivEREew_mi-smart-lock-pro.jpg'),
(165, 44, 'bRcGeZXOogxWvUL3BTrisQ_pms_1673923636.67345556.png'),
(166, 45, 'T40Hw4m7M39CGsSHNDCRUQ_9264103.jpg'),
(167, 45, '_2Fv0_Sfoqw11XmzVMHLAg_71jNr0MoZEL._AC_UF10001000_QL80_DpWeblab_.jpg'),
(168, 45, 'GTJdrqsMA9A65Cy7ZXFuhA_images_57.jpg'),
(169, 46, 'caKvy18KdWN5JYIKQjB9CA_images_60.jpg'),
(170, 46, 'PKQuX_p2j_a3Hwp5SZJ6sA_images_59.jpg'),
(171, 46, 'XYmk954OMGyTTeP6IglFXg_86c7bcbedfeb3307b505990300aee812.jpg'),
(172, 47, 'sFPtT63sa8vX-4MBpklVKQ_images_62.jpg'),
(173, 47, 'NO-h93nuDf7S3Z0zbHdvQA_71D3qc2L3mL._AC_UF8941000_QL80_.jpg'),
(174, 47, 'Nm10FvZciI5KdhO-IVcCCg_images_61.jpg'),
(175, 48, 'EXSXAoFFy2Gi2gF2jBC0YQ_images_64.jpg'),
(176, 48, 'yw9EHf0CckPxk0IfShbuPg_sg-11134201-23020-qsu3yk2khunvfc.jpg'),
(177, 48, 'Zg8VhkyxKsQ1IYd1yj3PEA_615H7BPmmL.jpg'),
(178, 49, 'nFuEeKgGiSYl_YNhk-vWXw_images_68.jpg'),
(179, 49, 'SRQ192H9ydFDP11nuqcmNg_images_67.jpg'),
(180, 49, 'e0EWZTPw-JB4UDkh4nL18A_images_66.jpg'),
(181, 50, 'qQTpNwvy9kE2Br-i0_53Iw_images_70.jpg'),
(182, 50, '2mDBrXRTlSpDy505N6Nc-w_61j-rRzFpyL._AC_UF10001000_QL80_.jpg'),
(183, 50, 'lj63UWxTN0VVNdAWyT83sQ_images_69.jpg'),
(184, 51, 'VGs_6ZDl0yBZgQE4gbmqkA_EOS-R10-18-45MM-G.jpg'),
(185, 51, '_mR9_h64pzv8sAYCnOQ1Og_sg-11134201-22110-8acpkfbljljv1a.jpg'),
(186, 51, 'y9b5eB9uLjKxYPTWvEKaHg_Screenshot_2025-05-28_142827.png'),
(187, 51, 'aTXHa2hWKPvGNzksizkhHQ_EOS-R10-18-45MM-E.jpg'),
(188, 51, 'KaS8gh5rX0MQZ28VgPiY0w_Screenshot_2025-05-28_142809.png'),
(189, 52, 'm8oidiXs6kBjg970b_2HvA_Nikon_Z50.jpeg'),
(190, 52, 'gqZtjbACmeHDiBZrQxSYcA_Screenshot_2025-05-28_143418.png'),
(191, 52, 'Vsd49FEKaX5HylEn_U8RmA_Nikon-Z50-16-50mm-kit-5-800x800.jpg'),
(192, 52, 'wEFcDQmIYMrcpGVwIC83aQ_Screenshot_2025-05-28_143357.png'),
(193, 53, 'oibDlULuF2Zbaev-OgK9Vg_Screenshot_2025-05-28_143749.png'),
(194, 53, '_wuGSJHlqOu0YYPAKdbyUQ_Screenshot_2025-05-28_143736.png'),
(195, 53, 'nAhSzmGl96oTkvY4afOsyw_Screenshot_2025-05-28_143709.png'),
(196, 53, 'Tsvq9QJolkwEvGwLuDl_jw_Screenshot_2025-05-28_143647.png');

-- --------------------------------------------------------

--
-- Table structure for table `product_info`
--

CREATE TABLE `product_info` (
  `product_info_id` int(11) NOT NULL,
  `product_category` varchar(50) NOT NULL,
  `product_name` varchar(100) NOT NULL,
  `product_description` text NOT NULL,
  `product_main_pic` varchar(299) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `product_info`
--

INSERT INTO `product_info` (`product_info_id`, `product_category`, `product_name`, `product_description`, `product_main_pic`) VALUES
(1, 'Mobile Phones', 'Samsung Galaxy A55 5G', 'Experience flagship features with the Samsung Galaxy A55 5G – equipped with a brilliant Super AMOLED display, long-lasting battery, and powerful Exynos processor. Comes with FREE jelly case, tempered glass, and SIM ejector tool. Backed with a 1-year Samsung warranty.', 'ww94q2oyEYdNN3GVSvuUMw_download_6.jpg'),
(2, 'Laptop', 'Acer Aspire 7 Gaming Laptop (2024)', 'Unleash productivity and power gaming with the Acer Aspire 7 featuring a Ryzen 7 CPU and NVIDIA GTX 1650 GPU. Ideal for students, creatives, and gamers. FREE laptop backpack, mouse, and MS Office Trial. Includes a 2-year Acer warranty (parts/labor).', 'G17FIKhtdnJu1-gv8CrQsg_DCOXWWgtDU2qBJkDCGon_Acer-Aspire-7_TomorrowsIndia.jpg'),
(4, 'Desktop', 'Intel Core i5 Pro Gaming Tower (Bundle Set)', 'Dominate online games and breeze through heavy workloads with this prebuilt Intel Core i5 gaming desktop. Comes with FREE RGB keyboard + mouse combo, and mousepad. 1-year parts and service warranty included.', 'N2P_29befD0LpgF-lKP1OA_5b77d3d548671fc904362a1df142f515.jpg'),
(5, 'Mobile Phones', 'realme Note 50', 'A perfect entry-level phone with a stylish build, big display, and smooth performance. Ideal for students and budget-conscious users. FREE realme SIM, protective case, and film. Includes 1-year realme warranty.', 'XRKG8tAjLb7tjG0cYsQYnw_images_14.jpg'),
(6, 'Mobile Phones', 'Xiaomi Redmi Note 13 5G', 'Stylish, slim, and fast – the Redmi Note 13 5G offers excellent value with AMOLED display and MediaTek power. Comes with FREE screen protector and silicone case. Includes 1-year Xiaomi warranty.', 'nLeinrZd18YlaEmBa9Ob1Q_m-note13-kv.jpg'),
(7, 'Mobile Phones', 'Infinix Zero 30 4G', 'Create cinematic vlogs and enjoy an ultra-smooth screen. FREE Type-C cable, jelly case, and SIM ejector. Covered by 1-year Infinix warranty.', 'UEWLxahWH9JQp50wrN68og_infinix-zero-30-4G-white.jpg'),
(8, 'Mobile Phones', 'Tecno Spark 20 Pro', 'Built for style and selfies – the Vivo Y100 offers 80W charging and a trendy design. Includes FREE phone stand, tempered glass, and vivo pouch. 1-year vivo warranty.', 'LNKYdCn0KYbLyO7jdeDmYg_gsmarena_003.jpg'),
(9, 'Mobile Phones', 'HONOR X8b', 'Feather-light with a powerful camera and bright AMOLED screen. Includes FREE charger brick, clear case, and film protector. 1-year official HONOR warranty.', 'rH7Bv6-IOrHYdcDShrcp-g_point1.jpg'),
(10, 'Mobile Phones', 'POCO X6 Pro 5G', 'Gaming beast with flagship power and vivid display. Comes with FREE fan grip, screen guard, and USB-C cable. 1-year POCO warranty.', 'SI1eeSg3zU0M39_sdzwKdQ_ph-11134207-7r98w-lqe848pq30e3a8.jpg'),
(11, 'Mobile Phones', 'Vivo Y100', 'Built for style and selfies – the Vivo Y100 offers 80W charging and a trendy design. Includes FREE phone stand, tempered glass, and vivo pouch. 1-year vivo warranty.', 'ZYfBtLD0mrl3jfvMJ9nH5Q_610cjhPdq3L.jpg'),
(12, 'Laptop', 'Acer Aspire 3 Slim', 'A dependable everyday laptop designed for students and professionals. FREE mouse and laptop sleeve. Backed by a 2-year Acer warranty.', 'qOi3UYY9twIQC8B_Epg2HA_4jyobCVKNGsuwqvwe6T7ri.png'),
(13, 'Laptop', 'Lenovo IdeaPad Slim 3', 'A thin and light laptop that’s perfect for students. FREE Lenovo backpack and pre-installed MS Office Home & Student 2021. 2-year Lenovo warranty.', 'm4xPMJZTieYU792j0aVlYw_Screenshot_2025-05-28_113140.png'),
(14, 'Laptop', 'MSI Modern 14', 'Compact and lightweight for mobility with power. FREE MSI mouse and laptop sleeve. 1-year warranty by MSI Philippines.', 'gDwyuqfr-FBzO72fTwFF-g_images_24.jpg'),
(15, 'Laptop', 'Apple MacBook Air M1', 'Powerfully quiet and ultra-thin. Perfect for creative work and productivity. FREE Type-C to USB Adapter and soft pouch. 1-year Apple warranty.', 'A53QnfrGZ2Yk0mTc8vG53w_gPvyaz76tASn87RCGuSdDc.jpg'),
(16, 'Laptop', 'Huawei MateBook D14', 'Metal-body laptop with fingerprint power button. Includes FREE Huawei backpack, Bluetooth mouse, and MS Office Home & Student 2021. 2-year warranty.', 'GOBFTlv2kyh35HDZ4S6PRw_s-l1200_1.jpg'),
(17, 'Laptop', 'Dell Inspiron 14 5430', 'A premium ultrabook for professionals and students with sleek aluminum finish. FREE Dell laptop bag and wireless mouse. Backed by 2-year Dell Premium Support.', 'sMSqMSTSO_tYv6B5E4LHRw_images_27.jpg'),
(18, 'Laptop', 'Gigabyte G5 KF Gaming Laptop', 'Affordable performance laptop with RTX 4060 for serious gaming and rendering. FREE gaming backpack and cooling pad. Includes 1-year Gigabyte service warranty.', '5uz_1s7pfywz5LSnpEcS2w_Screenshot_2025-05-28_115725.png'),
(19, 'Desktop', 'ASUS S500SC Desktop Tower', 'A sleek and compact desktop for home and office. FREE USB keyboard and mouse. 3-year ASUS warranty.', 'P5CVM3q-3HAngmckJigcAQ_Screenshot_2025-05-28_120303.png'),
(20, 'Desktop', 'Dell Inspiron 3020', 'Everyday performance in a compact chassis. FREE wired mouse and Dell keyboard. 1-year Dell onsite warranty.', 'p-OqDUzPCXE6BE7l1bxTDw_Screenshot_2025-05-28_120637.png'),
(21, 'Desktop', 'HP Pavilion TP01', 'A high-performance desktop PC for multitasking and productivity. FREE wired speaker and HP mouse. 2-year HP warranty.', '08rlEQJrtXhbtudwVd1hIg_images_29.jpg'),
(22, 'Desktop', 'Lenovo IdeaCentre 3', 'Perfect for families or students. FREE Lenovo USB keyboard and mouse. 1-year Lenovo depot warranty.', 'VXIcAbOmrYwLHbBVgUnbLA_Screenshot_2025-05-28_121252.png'),
(23, 'Desktop', 'MSI PRO DP21 Mini PC', 'Compact and powerful mini PC for workspaces. FREE MSI mousepad and wireless keyboard. 2-year warranty included.', 'Bq9YGiiH6hh1YgwSbL-sUw_ph-11134207-7r98r-ln2beobpttqf61.jpg'),
(24, 'Desktop', 'Gigabyte Brix Ultra-Compact PC', 'An energy-efficient ultra-compact desktop PC. FREE Gigabyte mouse. 1-year warranty provided.', 'i25MInR_cas-VZ6GAN_ZaA_download_23.jpg'),
(25, 'Desktop', 'Ryzen Budget Gamer', 'Custom-assembled desktop for gamers on a budget. FREE RGB keyboard and mouse. 6-month service warranty.', 'UvK7rZzdjInRZ_-R1H91lg_Screenshot_2025-05-28_122112.png'),
(26, 'Desktop', 'Intel i7 Performance Tower', 'All-around powerhouse for business and content creation. FREE webcam and UPS power supply. 1-year limited hardware warranty.', 'q6NgzmZt6XTgEzORqKosAg_81RRho7FyKL.jpg'),
(27, 'Audio Equipment', 'JBL Quantum 100 Gaming Wired Headset', 'Immersive sound for casual and competitive gaming. FREE headphone stand included. Covered by 1-year JBL warranty.', 'Q4vKVQhffrjjTWJxoI-ZMA_s-l1200_2.jpg'),
(28, 'Audio Equipment', 'Sony WH-CH520 Wireless Headphones', 'Comfortable on-ear headphones with long battery life. FREE travel pouch. 1-year Sony warranty.', 'SK0NiB1jr9AWQ3hYBfrRIQ_ph-11134207-7qul5-ljuoexob78un43.jpg'),
(29, 'Audio Equipment', 'Marshall Emberton II Bluetooth Speaker', 'Classic rock-inspired speaker with powerful sound. FREE sticker set and lanyard. 1-year limited warranty.', 'MGI6rj1qO9iZG0bRmKCbmw_Screenshot_2025-05-28_125958.png'),
(30, 'Audio Equipment', 'Maono AU-PM421 Condenser Microphone', 'Plug-and-play professional mic ideal for podcasts, streaming, and voiceovers. FREE pop filter and arm stand. 1-year warranty.', '0bkCTlFgmqbAnBhtEU-MFw_1ec601bd9eca5531397a1ed7a264cd7f.jpg'),
(31, 'Audio Equipment', 'Sennheiser HD 560S Open-Back Headphones', 'Audiophile-grade headphones with wide soundstage. FREE 6.3mm adapter. 2-year Sennheiser warranty.', 'Rcyf9zZnprm3HNuzRsw0Kg_ph-11134207-7r98o-lo4wx5xmzrru9f.jpg'),
(32, 'Audio Equipment', 'Edifier R1280DB Powered Bookshelf Speakers', 'Elegant wooden speakers with rich audio. FREE RCA cable included. 1-year Edifier warranty.', '9vsEmkbncsKXilddV3pKTw_Screenshot_2025-05-28_130910.png'),
(33, 'Audio Equipment', 'Logitech G435 LIGHTSPEED Wireless Gaming Headset', 'Lightweight wireless gaming headset with dual connectivity. FREE USB receiver case. 1-year Logitech warranty.', 'BR78HGGWRwpUJTTH2lbn9w_download_25.jpg'),
(34, 'Audio Equipment', 'RODE NT1 5th Gen Studio Microphone', 'Industry-standard condenser mic with USB-C and XLR output. FREE shock mount and dust cover. 10-year warranty with registration.', '6Dgdq319Mx_ggBzZsSt3yg_Screenshot_2025-05-28_132432.png'),
(35, 'Video Equipment', 'Logitech C920 HD Pro Webcam', 'Full HD webcam ideal for streaming and video conferencing. FREE tripod stand included. 2-year Logitech warranty.', 'Khd_r6vteMjN7WIQsxK43Q_download_30.jpg'),
(36, 'Video Equipment', 'Sony ZV-1F Vlog Camera', 'Compact and powerful camera for vloggers and content creators. FREE SD card and hand grip. 1-year Sony warranty.', 'k1dUIl2m39B8AMDIPGFWVA_maxresdefault_3.jpg'),
(37, 'Video Equipment', 'GoPro HERO11 Black', 'Waterproof action cam with ultra-wide lens. FREE extra battery and case. 1-year GoPro warranty.', '68ZU-8FBqH1p_LWOwTpx3w_images_39.jpg'),
(38, 'Video Equipment', 'Canon EOS M50 Mark II Mirrorless Camera', 'Lightweight mirrorless camera for photo and video. FREE 32GB SD card and camera bag. 1-year Canon warranty.', 'swYkPh7r_YMft0nlvNlMPQ_ph-11134207-7r98x-lv32pz28h7gyd8.jpg'),
(39, 'Video Equipment', 'Insta360 X3 360 Action Camera', 'Versatile 360° camera with waterproof body and AI editing. FREE invisible selfie stick. 1-year Insta360 warranty.', 'DWQmMdEMKVLDALYbW3RcIg_images_43.jpg'),
(40, 'Video Equipment', 'Elgato Cam Link 4K', 'Turn your DSLR or mirrorless camera into a webcam. FREE HDMI cable included. 2-year Elgato warranty.', 'PWZcrzG-Qio-LMhylksGAg_7bb52b28f125017a02b43d8240dc7d05.jpg'),
(41, 'Video Equipment', 'DJI Pocket 2 Creator Combo', 'Pocket-sized gimbal cam for smooth cinematic shots. FREE wrist strap and wide-angle lens. 1-year DJI warranty.', 'CY7TI48l9b1H0ySP-yKyWg_download_32.jpg'),
(42, 'Video Equipment', 'AverMedia PW513 4K Webcam', 'Pro-level 4K webcam with wide-angle lens and privacy shutter. FREE desk clip and cleaning cloth. 2-year warranty.', 'FdUmFsFOwiQGv1-FxMVh0w_PW513-3-600x597.jpg'),
(43, 'Smart Home Devices', 'Google Nest Hub (2nd Gen)', 'Smart display with Google Assistant and sleep tracking. FREE screen protector included. 1-year Google warranty.', '5EefqYxQCJHT2LgfKNMMkA_images_52.jpg'),
(44, 'Smart Home Devices', 'Xiaomi Smart Door Lock Pro', 'Advanced fingerprint smart lock with video doorbell. FREE installation guide. 1-year Xiaomi warranty.', 'SHMyUjpz_d6eIxGn5GejGg_images_55.jpg'),
(45, 'Smart Home Devices', 'Amazon Echo Dot (5th Gen)', 'Compact smart speaker with Alexa. FREE Echo wall mount. 1-year Amazon warranty.', '4y--Zi4TmYZrKTKrlmDhBA_81koUwaTQZL._AC_SL1500.jpg'),
(46, 'Smart Home Devices', 'Xiaomi Mi Smart Temperature & Humidity Monitor Clock', 'Minimalist climate monitor with LCD display. FREE adhesive wall mount. 1-year warranty.', 'KR2IQaOQTlWoEdE_1knHGQ_images_58.jpg'),
(47, 'Smart Home Devices', 'Samsung SmartThings Motion Sensor', 'Detects movement and automates home scenes. FREE magnetic mount. 1-year Samsung warranty.', 'XJTSEnypNlE50prVuDKrxg_g305MOTN1-o.jpg'),
(48, 'Smart Home Devices', 'Smart IR/RF Controller', 'Control IR and RF devices with a single app. FREE IR extender cable. 1-year BroadLink warranty.', 'IcCRCtT2WJeDNSBskZLXQg_images_63.jpg'),
(49, 'Smart Home Devices', 'Philips Hue White & Color Ambiance Bulb (E27)', '16 million colors with app and voice control. FREE Hue Bluetooth remote. 2-year Philips warranty.', 'qtchJDTE-eGL62l7piVT7g_images_65.jpg'),
(50, 'Smart Home Devices', 'TP-Link Tapo C210 Smart Security Camera', 'Full HD indoor security camera with night vision. FREE 32GB microSD card. 1-year TP-Link warranty.', 'PSWR7mN034N-yOGo2shfHg_77bdb4202bfbfd87b298495530296ea4.jpg_720x720q80.jpg'),
(51, 'Photography', 'Canon EOS R10 Mirrorless Camera', 'Lightweight mirrorless camera perfect for travel and street photography. FREE 64GB SD card & camera bag. 1-year Canon warranty.', 'Rx0QgoLjTqPew5ph4_gtPA_sg-11134201-22110-crsonnxtlljv6d.jpg'),
(52, 'Photography', 'Nikon Z50 Mirrorless Camera', 'Perfect for entry-level creators and vloggers. FREE mini tripod & 32GB SD card. 1-year Nikon warranty.', 'BKT4mRZ78QyKvMzi15CaKQ_NKNZ50KIT2_with_freebie-800x800.jpeg'),
(53, 'Photography', 'Fujifilm X-T30 II Mirrorless Camera', 'Retro-style compact camera for street & portrait photography. FREE leather strap & lens cap. 1-year Fujifilm warranty.', 'g3eXzTtxNBecvQ6J9nsI0w_Screenshot_2025-05-28_143632.png');

-- --------------------------------------------------------

--
-- Table structure for table `product_rating`
--

CREATE TABLE `product_rating` (
  `rating_id` int(11) NOT NULL,
  `shop_id` int(11) NOT NULL,
  `product_id` int(11) NOT NULL,
  `sender_id` int(11) NOT NULL,
  `rate` int(11) NOT NULL CHECK (`rate` between 1 and 5),
  `date_rated` datetime NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `product_rating`
--

INSERT INTO `product_rating` (`rating_id`, `shop_id`, `product_id`, `sender_id`, `rate`, `date_rated`) VALUES
(1, 1, 22, 2, 4, '2025-05-29 09:09:53'),
(2, 1, 13, 2, 4, '2025-05-29 09:10:03'),
(3, 1, 25, 2, 4, '2025-05-29 09:10:14'),
(4, 1, 4, 2, 3, '2025-05-29 09:10:27'),
(5, 1, 15, 2, 5, '2025-05-29 09:10:35'),
(6, 1, 8, 2, 5, '2025-05-29 09:16:01');

-- --------------------------------------------------------

--
-- Table structure for table `product_specs`
--

CREATE TABLE `product_specs` (
  `specs_id` int(11) NOT NULL,
  `product_info_id` int(11) NOT NULL,
  `specs_type` varchar(100) NOT NULL,
  `specs_content` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `product_specs`
--

INSERT INTO `product_specs` (`specs_id`, `product_info_id`, `specs_type`, `specs_content`) VALUES
(1, 1, '8GB RAM', '256GB Storage'),
(2, 1, 'Display: 6.6” FHD+ Super AMOLED, 120Hz Refresh Rate', 'Android 14, One UI 6'),
(3, 1, 'Rear Camera: Triple – 50MP (Main) + 12MP (Ultra-Wide) + 5MP (Macro)', 'Front Camera: 32MP'),
(4, 1, 'Connectivity: 5G, WiFi 6, Bluetooth 5.3, NFC', 'Biometrics: Under-display fingerprint, Face Unlock'),
(5, 2, 'Display: 15.6” FHD IPS Anti-Glare', 'Processor: AMD Ryzen 7 5825U'),
(6, 2, 'Graphics: NVIDIA GTX 1650 4GB GDDR6', 'RAM: Upgradable DDR4 up to 32GB'),
(7, 2, 'Storage: NVMe SSD, extra 2.5” SATA slot', 'Ports: USB-C, HDMI, 3x USB-A, Ethernet'),
(8, 2, 'Keyboard: Backlit, Numeric Keypad', 'OS: Windows 11 Home'),
(14, 4, 'Processor: Intel Core i5-12400F (6-core, 12-thread)', 'Graphics Card: GTX 1660 Super 6GB / RTX 3060 12GB'),
(15, 4, 'Motherboard: B660M Chipset, M.2 Slot, DDR4', 'RAM: 16GB DDR4 3200MHz (Expandable to 64GB)'),
(16, 4, 'Storage: 512GB NVMe SSD + 1TB HDD', 'Case: ATX Mid Tower with RGB Fans & Tempered Glass Side Panel'),
(17, 4, 'Power Supply: 650W Bronze Rated', 'Cooling: 4x RGB Fans, Air-cooled CPU'),
(18, 4, 'Operating System: Windows 11 Pro (Activated)', 'Connectivity: Gigabit LAN, WiFi USB Adapter included'),
(19, 5, 'Display: 6.74” HD+ IPS LCD, 90Hz', 'Processor: Unisoc T612 Octa-core'),
(20, 5, 'OS: Android 13 (Go Edition)', 'Rear Camera: 13MP AI Camera'),
(21, 5, 'Front Camera: 5MP', 'Battery: 5000mAh, 10W Charging'),
(22, 5, 'Fingerprint: Side-mounted', 'Dual SIM, microSD slot'),
(23, 6, 'Display: 6.6” FHD+ AMOLED, 120Hz', 'Processor: MediaTek Dimensity 6100+'),
(24, 6, 'Camera: 50MP + 2MP (Depth)', 'Front Camera: 8MP'),
(25, 6, 'Battery: 5000mAh, 33W Fast Charging', 'OS: Android 13, MIUI 14'),
(26, 7, 'Display: 6.78” FHD+ AMOLED, 120Hz', 'Processor: MediaTek Helio G99'),
(27, 7, 'Camera: 108MP Main Camera', 'Front Camera: 50MP Vlog Camera'),
(28, 7, 'Battery: 5000mAh, 45W Fast Charging', 'OS: XOS 13 (Android 13)'),
(29, 8, 'Display: 6.67” AMOLED, 120Hz', 'Processor: Qualcomm Snapdragon 685'),
(30, 8, 'Camera: 50MP + 2MP', 'Front Camera: 8MP'),
(31, 8, 'Battery: 5000mAh, 80W FlashCharge', 'OS: Funtouch OS 14 (Android 14)'),
(32, 9, 'Display: 6.7” AMOLED, 3240Hz PWM Dimming', 'Processor: Qualcomm Snapdragon 680'),
(33, 9, 'Camera: 108MP + 5MP + 2MP', 'Front Camera: 50MP Dual Light Selfie'),
(34, 9, 'Battery: 4500mAh, 35W Fast Charge', 'OS: MagicOS 7.2 (Android 13)'),
(35, 9, 'Side Fingerprint,', 'Slim 6.78mm'),
(36, 10, 'Display: 6.67” Flow AMOLED, 1.5K, 120Hz', 'Front Camera: 16MP'),
(37, 10, 'Processor: MediaTek Dimensity 8300-Ultra', 'Battery: 5000mAh, 67W Turbo Charge'),
(38, 10, 'Camera: 64MP OIS + 8MP + 2MP', 'OS: HyperOS (Android 14)'),
(39, 11, 'Display: 6.67” AMOLED, 120Hz', 'Processor: Qualcomm Snapdragon 685'),
(40, 11, 'Camera: 50MP + 2MP', 'Front Camera: 8MP'),
(41, 11, 'Battery: 5000mAh, 80W FlashCharge', 'OS: Funtouch OS 14 (Android 14)'),
(42, 11, 'IP54, Dual SIM,', 'MicroSD, Slim 7.79mm'),
(43, 12, 'Display', '15.6” FHD Anti-Glare'),
(44, 12, 'Processor', 'AMD Ryzen 3 5300U'),
(45, 12, 'Graphics', 'Radeon Integrated'),
(46, 12, 'RAM', '8GB DDR4'),
(47, 12, 'Storage', '512GB SSD'),
(48, 12, 'OS', 'Windows 11 Home'),
(49, 12, 'Battery', '41Wh, 3-cell Li-ion'),
(50, 13, 'Display', '15.6” FHD IPS, Anti-glare'),
(51, 13, 'Processor', 'Intel Core i3-13th Gen'),
(52, 13, 'Graphics', 'Intel UHD'),
(53, 13, 'RAM', '8GB DDR4'),
(54, 13, 'Storage', '256GB SSD'),
(55, 13, 'OS', 'Windows 11 Home'),
(56, 13, 'Battery', 'Up to 8 hours'),
(57, 14, 'Display', '14” FHD IPS-Level'),
(58, 14, 'Processor', 'Intel Core i5-12th Gen'),
(59, 14, 'Graphics', 'Intel Iris Xe'),
(60, 14, 'RAM', '8GB DDR4'),
(61, 14, 'Storage', '512GB SSD'),
(62, 14, 'OS', 'Windows 11'),
(63, 14, 'Weight', '1.4kg'),
(64, 15, 'Display', '13.3” Retina Display'),
(65, 15, 'Processor', 'Apple M1 8-core CPU'),
(66, 15, 'Graphics', '7-core GPU'),
(67, 15, 'RAM', '8GB Unified Memory'),
(68, 15, 'Storage', '256GB SSD'),
(69, 15, 'OS', 'macOS Sonoma'),
(70, 15, 'Battery', 'Up to 18 hours'),
(71, 16, 'Display', '14” FHD IPS, 180° hinge'),
(72, 16, 'Processor', 'Intel Core i5-1240P'),
(73, 16, 'Graphics', 'Intel Iris Xe'),
(74, 16, 'RAM', '16GB LPDDR4x'),
(75, 16, 'Storage', '512GB SSD'),
(76, 16, 'OS', 'Windows 11'),
(77, 16, 'Ports', 'USB-C, USB-A, HDMI, 3.5mm jack'),
(78, 17, 'Display', '14” FHD+ 1920x1200, Anti-glare, 250 nits'),
(79, 17, 'Processor', 'Intel Core i5-1335U (10-core, 4.6GHz Max)'),
(80, 17, 'Graphics', 'Intel Iris Xe'),
(81, 17, 'RAM', '16GB LPDDR5'),
(82, 17, 'Storage', '512GB PCIe NVMe SSD'),
(83, 17, 'OS', 'Windows 11 Home'),
(84, 17, 'Ports', 'USB-C, HDMI 1.4, USB-A, Audio jack'),
(85, 17, 'Battery', '54Wh, ExpressCharge support'),
(86, 18, 'Display', '15.6” FHD, 144Hz IPS Anti-Glare'),
(87, 18, 'Processor', 'Intel Core i5-12500H (12-core)'),
(88, 18, 'Graphics', 'NVIDIA GeForce RTX 4060 8GB'),
(89, 18, 'RAM', '16GB DDR4 3200MHz'),
(90, 18, 'Storage', '512GB M.2 SSD'),
(91, 18, 'Cooling', 'WindForce dual-fan cooling system'),
(92, 18, 'OS', 'Windows 11 Home'),
(93, 18, 'Ports', 'USB-C, HDMI 2.1, USB-A, RJ-45, miniDP'),
(94, 19, 'Processor', 'Intel Core i5-12400'),
(95, 19, 'Graphics', 'Intel UHD 730'),
(96, 19, 'RAM', '8GB DDR4'),
(97, 19, 'Storage', '512GB NVMe SSD'),
(98, 19, 'OS', 'Windows 11 Home'),
(99, 19, 'Ports', 'USB 3.2, HDMI, VGA, RJ45'),
(100, 19, 'Wi-Fi', 'Yes (WiFi 5)'),
(101, 20, 'Processor', 'Intel Core i3-13100'),
(102, 20, 'Graphics', 'Intel UHD 730'),
(103, 20, 'RAM', '8GB DDR4'),
(104, 20, 'Storage', '1TB HDD'),
(105, 20, 'OS', 'Windows 11'),
(106, 20, 'Ports', 'USB 3.2, HDMI, Ethernet'),
(107, 20, 'Wi-Fi', 'Yes'),
(108, 21, 'Processor', 'AMD Ryzen 5 5600G'),
(109, 21, 'Graphics', 'Radeon Vega 7'),
(110, 21, 'RAM', '8GB DDR4'),
(111, 21, 'Storage', '512GB SSD'),
(112, 21, 'OS', 'Windows 11 Home'),
(113, 21, 'Wi-Fi', 'WiFi 5 + Bluetooth'),
(114, 22, 'Processor', 'AMD Ryzen 3 5300G'),
(115, 22, 'Graphics', 'Radeon Vega'),
(116, 22, 'RAM', '8GB DDR4'),
(117, 22, 'Storage', '256GB SSD + 1TB HDD'),
(118, 22, 'OS', 'Windows 11 Home'),
(119, 22, 'Ports', 'USB-A, HDMI, VGA, SD card'),
(120, 22, 'Wi-Fi', 'Yes'),
(121, 23, 'Processor', 'Intel Core i5-12400'),
(122, 23, 'Graphics', 'Intel UHD 730'),
(123, 23, 'RAM', '8GB DDR4'),
(124, 23, 'Storage', '512GB SSD'),
(125, 23, 'OS', 'Windows 11'),
(126, 23, 'Ports', 'USB 3.2, DisplayPort, HDMI'),
(127, 24, 'Processor', 'Intel Celeron N5105'),
(128, 24, 'Graphics', 'Intel UHD'),
(129, 24, 'RAM', '8GB DDR4'),
(130, 24, 'Storage', '256GB M.2 SSD'),
(131, 24, 'OS', 'Windows 11'),
(132, 24, 'Ports', 'HDMI, VGA, USB 3.0, Ethernet'),
(133, 25, 'Processor', 'AMD Ryzen 5 4600G'),
(134, 25, 'Graphics', 'Radeon Vega 7'),
(135, 25, 'RAM', '16GB DDR4'),
(136, 25, 'Storage', '512GB SSD'),
(137, 25, 'Wi-Fi', 'USB WiFi Adapter included'),
(145, 26, 'Processor', 'Intel Core i7-12700'),
(146, 26, 'Graphics', 'Intel UHD 770'),
(147, 26, 'RAM', '16GB DDR4'),
(148, 26, 'Storage', '1TB NVMe SSD'),
(155, 28, 'Driver Size', '30mm'),
(156, 28, 'Battery Life', 'Up to 50 hours'),
(157, 28, 'Charging', 'USB-C'),
(158, 28, 'Bluetooth Version', '5.2'),
(159, 28, 'Voice Assistant Support', 'Yes'),
(160, 29, 'Battery Life', 'Up to 30 hours'),
(161, 29, 'Water Resistance', 'IP67'),
(162, 29, 'Charging', 'USB-C'),
(163, 29, 'Dimensions', '68 x 160 x 76 mm'),
(164, 29, 'Weight', '700g'),
(165, 29, 'Multi-Speaker Pairing', 'Yes (Stack Mode)'),
(166, 30, 'Microphone Type', 'Cardioid Condenser'),
(167, 30, 'Connection', 'USB 2.0'),
(168, 30, 'Frequency Response', '20Hz–20kHz'),
(169, 30, 'Sampling Rate', '192kHz/24-bit'),
(170, 30, 'Compatibility', 'Windows & macOS'),
(171, 30, 'Included', 'Shock mount, boom arm, pop filter'),
(172, 31, 'Driver Size', '38mm'),
(173, 31, 'Frequency Response', '6Hz – 38kHz'),
(174, 31, 'Impedance', '120 ohms'),
(175, 31, 'Cable Length', '3m detachable'),
(176, 31, 'Connection', '3.5mm + 6.3mm adapter'),
(177, 31, 'Weight', '240g'),
(178, 32, 'Output Power', '42W RMS'),
(179, 32, 'Inputs', 'RCA, Optical, Coaxial, Bluetooth'),
(180, 32, 'Tweeter', '13mm silk dome'),
(181, 32, 'Woofer', '4-inch'),
(182, 32, 'Remote Control', 'Included'),
(183, 32, 'Weight', '4.9kg (pair)'),
(184, 33, 'Wireless Range', '10m (2.4GHz & Bluetooth)'),
(185, 33, 'Battery Life', 'Up to 18 hours'),
(186, 33, 'Driver Size', '40mm'),
(187, 33, 'Microphone', 'Dual beamforming mic'),
(188, 33, 'Weight', '165g'),
(189, 33, 'Compatibility', 'PC, PS4, PS5, mobile'),
(190, 34, 'Polar Pattern', 'Cardioid'),
(191, 34, 'Frequency Range', '20Hz–20kHz'),
(192, 34, 'Connection', 'XLR & USB-C'),
(193, 34, 'Max SPL', '132dB'),
(194, 34, 'Extras', 'Shock mount, pop filter, USB cable'),
(195, 27, 'Driver Size', '40mm'),
(196, 27, 'Connection', '3.5mm audio jack'),
(197, 27, 'Microphone', 'Detachable boom mic'),
(198, 27, 'Compatibility', 'PC, PS, Xbox, Switch, Mobile'),
(199, 27, 'Weight', '220g'),
(200, 27, 'Extras', 'Volume control on earcup'),
(201, 35, 'Resolution: 1080p at 30fps', 'Field of View: 78°'),
(202, 35, 'Microphones: Dual stereo', 'Autofocus: Yes'),
(203, 35, 'Mounting: Universal clip + tripod support', 'Compatibility: Windows, macOS, ChromeOS'),
(204, 36, 'Sensor: 1.0-type Exmor RS CMOS', 'Lens: 20mm F2.0 fixed lens'),
(205, 36, 'Video: 4K30fps / 1080p120fps', 'Display: Flip-out LCD'),
(206, 36, 'Mic: Directional 3-capsule', 'Connectivity: USB-C, Wi-Fi, Bluetooth'),
(207, 37, 'Video: 5.3K60 / 4K120', 'Stabilization: HyperSmooth 5.0'),
(208, 37, 'Waterproof: Up to 10m', 'Battery: Enduro 1720mAh'),
(209, 37, 'Mounting: Built-in folding fingers', 'Voice Control: Yes'),
(210, 38, 'Sensor: APS-C CMOS 24.1MP', 'Autofocus: Dual Pixel AF'),
(211, 38, 'Video: 4K24fps, 1080p60fps', 'LCD: 3.0\" Vari-Angle Touchscreen'),
(212, 38, 'Microphone Input: Yes', 'Connectivity: Wi-Fi, Bluetooth'),
(213, 39, 'Video: 5.7K 360°, 4K single-lens', 'Waterproof: Up to 10m'),
(214, 39, 'Display: 2.29\" Touchscreen', 'Battery: 1800mAh'),
(215, 39, 'Stabilization: FlowState', 'Connectivity: USB-C, Bluetooth, Wi-Fi'),
(216, 40, 'Input: HDMI (uncompressed video)', 'Output: USB 3.0'),
(217, 40, 'Supported Resolutions: Up to 4K30, 1080p60', 'Plug & Play: Yes'),
(218, 40, 'Compatibility: OBS, Zoom, Skype, Teams', 'OS Support: Windows & macOS'),
(219, 41, 'Camera: 64MP photo / 4K60 video', 'Audio: 4-mic system'),
(220, 41, 'Stabilizer: 3-axis gimbal', 'Display: Built-in touchscreen'),
(221, 41, 'Battery Life: Up to 140 mins', 'Accessories Included: Mic, tripod, control wheel'),
(222, 42, 'Resolution: 4K30fps, 1080p60fps', 'Microphone: Dual stereo'),
(223, 42, 'Mounting: Tripod-compatible', 'USB Type: USB 3.0 Type-C'),
(224, 42, 'Lens: Wide-angle 94° FOV', 'AI Features: Auto framing, HDR'),
(225, 43, 'Display: 7” touchscreen', 'Voice Assistant: Google Assistant'),
(226, 43, 'Sensors: Soli radar for sleep sensing', 'Connectivity: Wi-Fi, Bluetooth 5.0'),
(227, 43, 'Speaker: Full-range', 'Smart HoSmart Home Control: Lights, cameras, etc.me Control: Lights, cameras, etc.'),
(228, 44, 'Unlock Methods: Fingerprint, password, NFC, mechanical key', 'Alerts: Tamper and unlock logs'),
(229, 44, 'Camera: 1080p wide-angle', 'Battery: Rechargeable lithium (USB-C)'),
(230, 45, 'Speaker Type: 1.73” front-firing', 'Connectivity: Dual-band Wi-Fi, Bluetooth'),
(231, 45, 'Connectivity: Dual-band Wi-Fi, Bluetooth', 'Sensors: Temperature, motion'),
(232, 45, 'mart Home Control: Lights,', 'routine'),
(233, 46, 'Display: 3.7” e-ink screen', 'Smart Integration: BLE, Mi Home'),
(234, 46, 'Sensors: Temp & humidity precision sensor', 'Battery: CR2032 button cell'),
(235, 47, 'Detection Range: Up to 5m', 'Battery Life: Up to 1 year'),
(236, 47, 'Connectivity: Zigbee 3.0', 'Smart Integration: SmartThings app'),
(237, 48, 'Supported Devices: TVs, ACs, fans, etc.', 'Control Methods: App, voice (Alexa, Google)'),
(238, 48, 'Range: Up to 8m IR / 20m RF', 'Power: Micro USB'),
(239, 49, 'Wattage: 10W (60W equivalent)', 'Connectivity: Zigbee + Bluetooth'),
(240, 49, 'Lifespan: 25,000 hours', 'Control: Hue App, Alexa, Google'),
(241, 50, 'Video: 2K QHD', 'Pan/Tilt: 360° horizontal, 114° vertical'),
(242, 50, 'Night Vision: Infrared', 'Storage: Cloud & microSD up to 256GB'),
(243, 50, 'Motion Detection: Yes', 'Voice Control: Alexa, Google'),
(244, 51, 'Sensor', '24.2MP APS-C CMOS'),
(245, 51, 'Processor', 'DIGIC X'),
(246, 51, 'Video', '4K60 / FHD120'),
(247, 51, 'AF System', 'Dual Pixel CMOS AF II'),
(248, 51, 'Burst Shooting', '15fps Mechanical'),
(249, 51, 'Connectivity', 'Wi-Fi, Bluetooth'),
(250, 52, 'Sensor', '20.9MP APS-C'),
(251, 52, 'Video', '4K30 / FHD120'),
(252, 52, 'Screen', '3.2\" Flip-down Touch LCD'),
(253, 52, 'AF System', '209-point hybrid'),
(254, 52, 'ISO Range', '100–51200'),
(255, 52, 'Wi-Fi / Bluetooth', 'Yes'),
(256, 53, 'Sensor', '26.1MP X-Trans CMOS 4'),
(257, 53, 'Video', '4K30 / FHD120'),
(258, 53, 'Focus Points', '425 AF points'),
(259, 53, 'Screen', '3” Tilt Touchscreen'),
(260, 53, 'Burst', '8fps (Mech), 30fps (Elec)'),
(261, 53, 'Wireless', 'Wi-Fi, Bluetooth');

-- --------------------------------------------------------

--
-- Table structure for table `product_variant_images`
--

CREATE TABLE `product_variant_images` (
  `images_id` int(11) NOT NULL,
  `product_id` int(11) NOT NULL,
  `product_image` varchar(299) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `seller_sales`
--

CREATE TABLE `seller_sales` (
  `sales_id` int(11) NOT NULL,
  `seller_id` int(11) NOT NULL,
  `order_id` int(11) NOT NULL,
  `sale` decimal(10,2) NOT NULL,
  `date_created` datetime NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `seller_sales`
--

INSERT INTO `seller_sales` (`sales_id`, `seller_id`, `order_id`, `sale`, `date_created`) VALUES
(1, 3, 2, 18399.08, '2025-05-29 09:09:34'),
(2, 3, 4, 35879.08, '2025-05-29 09:09:39'),
(3, 3, 5, 9199.08, '2025-05-29 09:09:42'),
(4, 3, 6, 17478.16, '2025-05-29 09:09:46'),
(5, 3, 1, 11499.08, '2025-05-29 09:09:48'),
(6, 3, 7, 59800.00, '2025-05-29 09:15:57');

-- --------------------------------------------------------

--
-- Table structure for table `seller_vouchers`
--

CREATE TABLE `seller_vouchers` (
  `voucher_id` int(11) NOT NULL,
  `seller_id` int(11) NOT NULL,
  `voucher_type` varchar(30) NOT NULL,
  `voucher_name` varchar(255) NOT NULL,
  `voucher_description` text DEFAULT NULL,
  `voucher_min_spend` decimal(10,2) NOT NULL,
  `voucher_value` decimal(10,2) DEFAULT 0.00,
  `voucher_start_date` date NOT NULL,
  `voucher_end_date` date NOT NULL,
  `status` varchar(50) NOT NULL,
  `date_added` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `shop`
--

CREATE TABLE `shop` (
  `shop_id` int(11) NOT NULL,
  `shop_info_id` int(11) NOT NULL,
  `seller_id` int(11) NOT NULL,
  `date_created` datetime NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `shop`
--

INSERT INTO `shop` (`shop_id`, `shop_info_id`, `seller_id`, `date_created`) VALUES
(1, 1, 3, '2025-05-27 20:40:32'),
(2, 2, 13, '2025-05-28 02:34:28'),
(3, 3, 14, '2025-05-28 02:44:38'),
(4, 4, 15, '2025-05-28 02:53:14'),
(5, 5, 16, '2025-05-28 03:03:06');

-- --------------------------------------------------------

--
-- Table structure for table `shop_info`
--

CREATE TABLE `shop_info` (
  `shop_info_id` int(11) NOT NULL,
  `shop_name` varchar(100) NOT NULL,
  `shop_description` text NOT NULL,
  `shop_pic` varchar(299) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `shop_info`
--

INSERT INTO `shop_info` (`shop_info_id`, `shop_name`, `shop_description`, `shop_pic`) VALUES
(1, 'Zack Shop', 'Zack Shop is an online shopping destination specializing in the latest technology and gadgets. From smartphones and laptops to smart accessories, we offer a wide range of high-quality products at competitive prices. Enjoy secure checkout, fast delivery, and excellent customer support with every purchase.', 'FiVHBUBUJx5YaJMAxq1hSw_images_1.png'),
(2, 'TechHustle PH', 'TechHustle PH delivers top-notch gadgets and gear to Filipino techies nationwide. Discover innovation, affordability, and speed all in one digital space.', 'jnKxKiIkPGUXVgOc1uCQRA_download.png'),
(3, 'DigitalEase', 'DigitalEase is your go-to shop for seamless online tech shopping. We bring premium electronics closer to home with trust, speed, and creativity.', 'T5UhJlTuR4EJoSFOPyzfSw_download_1.png'),
(4, 'PinoyGizmo', 'PinoyGizmo combines Filipino passion with cutting-edge gadgets. Experience tech that empowers your lifestyle—trusted, tested, and delivered with heart.', 'fWrdLmqbq1kH4SeDyYoolQ_download_2.png'),
(5, 'GadgetGlow', 'GadgetGlow brings a spark of innovation to your tech journey. With handpicked electronics, we brighten your digital world one gadget at a time.', '_ylF9MUbepHpsDLOBNS3Cg_images_2.png');

-- --------------------------------------------------------

--
-- Table structure for table `shop_listing`
--

CREATE TABLE `shop_listing` (
  `shop_listing_id` int(11) NOT NULL,
  `shop_id` int(11) NOT NULL,
  `seller_id` int(11) NOT NULL,
  `product_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `shop_listing`
--

INSERT INTO `shop_listing` (`shop_listing_id`, `shop_id`, `seller_id`, `product_id`) VALUES
(1, 1, 3, 1),
(2, 1, 3, 2),
(3, 1, 3, 3),
(4, 1, 3, 4),
(5, 1, 3, 5),
(8, 1, 3, 8),
(9, 1, 3, 9),
(10, 1, 3, 10),
(11, 1, 3, 11),
(12, 1, 3, 12),
(13, 1, 3, 13),
(14, 1, 3, 14),
(15, 1, 3, 15),
(16, 1, 3, 16),
(17, 1, 3, 17),
(18, 1, 3, 18),
(19, 1, 3, 19),
(20, 1, 3, 20),
(21, 1, 3, 21),
(22, 1, 3, 22),
(23, 1, 3, 23),
(24, 1, 3, 24),
(25, 1, 3, 25),
(26, 1, 3, 26),
(27, 2, 13, 27),
(28, 2, 13, 28),
(29, 2, 13, 29),
(30, 2, 13, 30),
(31, 2, 13, 31),
(32, 2, 13, 32),
(33, 2, 13, 33),
(34, 2, 13, 34),
(35, 2, 13, 35),
(36, 2, 13, 36),
(37, 2, 13, 37),
(38, 2, 13, 38),
(39, 2, 13, 39),
(40, 2, 13, 40),
(41, 2, 13, 41),
(42, 3, 14, 42),
(43, 3, 14, 43),
(44, 3, 14, 44),
(45, 3, 14, 45),
(46, 3, 14, 46),
(47, 3, 14, 47),
(48, 3, 14, 48),
(49, 3, 14, 49),
(50, 3, 14, 50),
(51, 4, 15, 51),
(52, 4, 15, 52),
(53, 4, 15, 53),
(54, 4, 15, 54),
(55, 4, 15, 55),
(56, 4, 15, 56),
(57, 4, 15, 57),
(58, 4, 15, 58),
(59, 4, 15, 59),
(60, 4, 15, 60),
(61, 4, 15, 61),
(62, 4, 15, 62),
(63, 4, 15, 63),
(64, 4, 15, 64),
(65, 4, 15, 65),
(66, 5, 16, 66),
(67, 5, 16, 67),
(68, 5, 16, 68),
(69, 5, 16, 69),
(70, 5, 16, 70),
(71, 5, 16, 71),
(72, 5, 16, 72),
(73, 5, 16, 73),
(74, 5, 16, 74),
(75, 5, 16, 75),
(76, 1, 3, 76),
(77, 1, 3, 77),
(78, 1, 3, 78),
(79, 1, 3, 79),
(80, 1, 3, 80),
(81, 1, 3, 81),
(82, 1, 3, 82),
(83, 1, 3, 83),
(84, 1, 3, 84),
(85, 1, 3, 85),
(86, 1, 3, 86),
(87, 1, 3, 87),
(88, 2, 13, 88),
(89, 2, 13, 89),
(90, 2, 13, 90),
(91, 2, 13, 91),
(92, 2, 13, 92);

-- --------------------------------------------------------

--
-- Table structure for table `user_account`
--

CREATE TABLE `user_account` (
  `user_id` int(11) NOT NULL,
  `personal_id` int(11) NOT NULL,
  `address_id` int(11) NOT NULL,
  `valid_id` int(11) NOT NULL,
  `contact_id` int(11) NOT NULL,
  `login_id` int(11) NOT NULL,
  `business_id` int(11) DEFAULT NULL,
  `user_role` enum('Buyer','Seller','Admin','Courier') NOT NULL,
  `profile_pic` varchar(299) DEFAULT NULL,
  `status` enum('Pending','Approved','Declined','Banned','Suspended','Archived') NOT NULL DEFAULT 'Pending',
  `date_created` datetime NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `user_account`
--

INSERT INTO `user_account` (`user_id`, `personal_id`, `address_id`, `valid_id`, `contact_id`, `login_id`, `business_id`, `user_role`, `profile_pic`, `status`, `date_created`) VALUES
(1, 1, 1, 1, 1, 1, NULL, 'Admin', NULL, 'Approved', '2025-05-27 20:34:35'),
(2, 8, 8, 2, 8, 2, NULL, 'Buyer', 'olJSO9ny7PSeYSzFcfxoGQ_p9957510_k_h9_ab.jpg', 'Approved', '2025-05-27 20:38:22'),
(3, 9, 9, 3, 9, 3, 1, 'Seller', NULL, 'Approved', '2025-05-27 20:40:32'),
(4, 10, 10, 4, 10, 4, NULL, 'Courier', NULL, 'Approved', '2025-05-27 20:42:19'),
(5, 11, 11, 5, 11, 5, NULL, 'Buyer', NULL, 'Approved', '2025-05-28 02:08:00'),
(6, 12, 12, 6, 12, 6, NULL, 'Buyer', NULL, 'Approved', '2025-05-28 02:11:39'),
(7, 13, 13, 7, 13, 7, NULL, 'Buyer', NULL, 'Approved', '2025-05-28 02:14:17'),
(8, 14, 14, 8, 14, 8, NULL, 'Buyer', NULL, 'Approved', '2025-05-28 02:17:23'),
(9, 15, 15, 9, 15, 9, NULL, 'Courier', NULL, 'Approved', '2025-05-28 02:21:00'),
(10, 16, 16, 10, 16, 10, NULL, 'Courier', NULL, 'Approved', '2025-05-28 02:23:18'),
(11, 17, 17, 11, 17, 11, NULL, 'Courier', NULL, 'Approved', '2025-05-28 02:26:43'),
(12, 18, 18, 12, 18, 12, NULL, 'Courier', NULL, 'Approved', '2025-05-28 02:28:50'),
(13, 19, 19, 13, 19, 13, 2, 'Seller', NULL, 'Approved', '2025-05-28 02:34:28'),
(14, 20, 20, 14, 20, 14, 3, 'Seller', NULL, 'Approved', '2025-05-28 02:44:38'),
(15, 22, 22, 15, 22, 15, 4, 'Seller', NULL, 'Approved', '2025-05-28 02:53:14'),
(16, 23, 23, 16, 23, 16, 5, 'Seller', NULL, 'Approved', '2025-05-28 03:03:06');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `account_address_info`
--
ALTER TABLE `account_address_info`
  ADD PRIMARY KEY (`address_id`);

--
-- Indexes for table `account_business_info`
--
ALTER TABLE `account_business_info`
  ADD PRIMARY KEY (`business_id`);

--
-- Indexes for table `account_contact_info`
--
ALTER TABLE `account_contact_info`
  ADD PRIMARY KEY (`contact_id`),
  ADD UNIQUE KEY `email` (`email`),
  ADD UNIQUE KEY `phone` (`phone`);

--
-- Indexes for table `account_login_info`
--
ALTER TABLE `account_login_info`
  ADD PRIMARY KEY (`login_id`),
  ADD UNIQUE KEY `username` (`username`);

--
-- Indexes for table `account_personal_info`
--
ALTER TABLE `account_personal_info`
  ADD PRIMARY KEY (`personal_id`);

--
-- Indexes for table `account_valid_info`
--
ALTER TABLE `account_valid_info`
  ADD PRIMARY KEY (`valid_id`),
  ADD UNIQUE KEY `id_no` (`id_no`);

--
-- Indexes for table `admin_order_commission`
--
ALTER TABLE `admin_order_commission`
  ADD PRIMARY KEY (`commission_id`),
  ADD KEY `order_id` (`order_id`),
  ADD KEY `seller_id` (`seller_id`);

--
-- Indexes for table `admin_sales`
--
ALTER TABLE `admin_sales`
  ADD PRIMARY KEY (`sales_id`),
  ADD KEY `admin_id` (`admin_id`),
  ADD KEY `user_id` (`user_id`),
  ADD KEY `order_id` (`order_id`);

--
-- Indexes for table `buyer_cart`
--
ALTER TABLE `buyer_cart`
  ADD PRIMARY KEY (`cart_id`),
  ADD KEY `product_id` (`product_id`),
  ADD KEY `buyer_id` (`buyer_id`);

--
-- Indexes for table `buyer_like`
--
ALTER TABLE `buyer_like`
  ADD PRIMARY KEY (`like_id`),
  ADD KEY `product_info_id` (`product_info_id`),
  ADD KEY `buyer_id` (`buyer_id`);

--
-- Indexes for table `buyer_order`
--
ALTER TABLE `buyer_order`
  ADD PRIMARY KEY (`order_id`),
  ADD KEY `shop_id` (`shop_id`),
  ADD KEY `seller_id` (`seller_id`),
  ADD KEY `product_id` (`product_id`),
  ADD KEY `buyer_id` (`buyer_id`);

--
-- Indexes for table `courier_sales`
--
ALTER TABLE `courier_sales`
  ADD PRIMARY KEY (`sales_id`),
  ADD KEY `order_id` (`order_id`),
  ADD KEY `courier_id` (`courier_id`);

--
-- Indexes for table `login_attempts`
--
ALTER TABLE `login_attempts`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `messages`
--
ALTER TABLE `messages`
  ADD PRIMARY KEY (`message_id`),
  ADD KEY `recipient_id` (`recipient_id`),
  ADD KEY `sender_id` (`sender_id`);

--
-- Indexes for table `notifications`
--
ALTER TABLE `notifications`
  ADD PRIMARY KEY (`notification_id`),
  ADD KEY `recipient_id` (`recipient_id`),
  ADD KEY `sender_id` (`sender_id`);

--
-- Indexes for table `order_completed`
--
ALTER TABLE `order_completed`
  ADD PRIMARY KEY (`completed_id`),
  ADD KEY `order_id` (`order_id`);

--
-- Indexes for table `order_delivery`
--
ALTER TABLE `order_delivery`
  ADD PRIMARY KEY (`delivery_id`),
  ADD KEY `order_id` (`order_id`),
  ADD KEY `courier_id` (`courier_id`);

--
-- Indexes for table `order_packing`
--
ALTER TABLE `order_packing`
  ADD PRIMARY KEY (`packing_id`),
  ADD KEY `order_id` (`order_id`);

--
-- Indexes for table `order_received`
--
ALTER TABLE `order_received`
  ADD PRIMARY KEY (`received_id`),
  ADD KEY `order_id` (`order_id`),
  ADD KEY `buyer_id` (`buyer_id`);

--
-- Indexes for table `order_shipping`
--
ALTER TABLE `order_shipping`
  ADD PRIMARY KEY (`shipping_id`),
  ADD KEY `order_id` (`order_id`);

--
-- Indexes for table `product`
--
ALTER TABLE `product`
  ADD PRIMARY KEY (`product_id`),
  ADD KEY `product_info_id` (`product_info_id`);

--
-- Indexes for table `product_feedback`
--
ALTER TABLE `product_feedback`
  ADD PRIMARY KEY (`feedback_id`),
  ADD KEY `shop_id` (`shop_id`),
  ADD KEY `product_id` (`product_id`),
  ADD KEY `sender_id` (`sender_id`);

--
-- Indexes for table `product_images`
--
ALTER TABLE `product_images`
  ADD PRIMARY KEY (`images_id`),
  ADD KEY `product_info_id` (`product_info_id`);

--
-- Indexes for table `product_info`
--
ALTER TABLE `product_info`
  ADD PRIMARY KEY (`product_info_id`);

--
-- Indexes for table `product_rating`
--
ALTER TABLE `product_rating`
  ADD PRIMARY KEY (`rating_id`),
  ADD KEY `shop_id` (`shop_id`),
  ADD KEY `product_id` (`product_id`),
  ADD KEY `sender_id` (`sender_id`);

--
-- Indexes for table `product_specs`
--
ALTER TABLE `product_specs`
  ADD PRIMARY KEY (`specs_id`),
  ADD KEY `product_info_id` (`product_info_id`);

--
-- Indexes for table `product_variant_images`
--
ALTER TABLE `product_variant_images`
  ADD PRIMARY KEY (`images_id`),
  ADD KEY `product_id` (`product_id`);

--
-- Indexes for table `seller_sales`
--
ALTER TABLE `seller_sales`
  ADD PRIMARY KEY (`sales_id`),
  ADD KEY `order_id` (`order_id`),
  ADD KEY `seller_id` (`seller_id`);

--
-- Indexes for table `seller_vouchers`
--
ALTER TABLE `seller_vouchers`
  ADD PRIMARY KEY (`voucher_id`),
  ADD KEY `seller_id` (`seller_id`);

--
-- Indexes for table `shop`
--
ALTER TABLE `shop`
  ADD PRIMARY KEY (`shop_id`),
  ADD KEY `shop_info_id` (`shop_info_id`),
  ADD KEY `seller_id` (`seller_id`);

--
-- Indexes for table `shop_info`
--
ALTER TABLE `shop_info`
  ADD PRIMARY KEY (`shop_info_id`);

--
-- Indexes for table `shop_listing`
--
ALTER TABLE `shop_listing`
  ADD PRIMARY KEY (`shop_listing_id`),
  ADD KEY `shop_id` (`shop_id`),
  ADD KEY `seller_id` (`seller_id`),
  ADD KEY `product_id` (`product_id`);

--
-- Indexes for table `user_account`
--
ALTER TABLE `user_account`
  ADD PRIMARY KEY (`user_id`),
  ADD KEY `personal_id` (`personal_id`),
  ADD KEY `address_id` (`address_id`),
  ADD KEY `contact_id` (`contact_id`),
  ADD KEY `valid_id` (`valid_id`),
  ADD KEY `login_id` (`login_id`),
  ADD KEY `business_id` (`business_id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `account_address_info`
--
ALTER TABLE `account_address_info`
  MODIFY `address_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=24;

--
-- AUTO_INCREMENT for table `account_business_info`
--
ALTER TABLE `account_business_info`
  MODIFY `business_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT for table `account_contact_info`
--
ALTER TABLE `account_contact_info`
  MODIFY `contact_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=24;

--
-- AUTO_INCREMENT for table `account_login_info`
--
ALTER TABLE `account_login_info`
  MODIFY `login_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=17;

--
-- AUTO_INCREMENT for table `account_personal_info`
--
ALTER TABLE `account_personal_info`
  MODIFY `personal_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=24;

--
-- AUTO_INCREMENT for table `account_valid_info`
--
ALTER TABLE `account_valid_info`
  MODIFY `valid_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=17;

--
-- AUTO_INCREMENT for table `admin_order_commission`
--
ALTER TABLE `admin_order_commission`
  MODIFY `commission_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=13;

--
-- AUTO_INCREMENT for table `admin_sales`
--
ALTER TABLE `admin_sales`
  MODIFY `sales_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=13;

--
-- AUTO_INCREMENT for table `buyer_cart`
--
ALTER TABLE `buyer_cart`
  MODIFY `cart_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=12;

--
-- AUTO_INCREMENT for table `buyer_like`
--
ALTER TABLE `buyer_like`
  MODIFY `like_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT for table `buyer_order`
--
ALTER TABLE `buyer_order`
  MODIFY `order_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=8;

--
-- AUTO_INCREMENT for table `courier_sales`
--
ALTER TABLE `courier_sales`
  MODIFY `sales_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- AUTO_INCREMENT for table `login_attempts`
--
ALTER TABLE `login_attempts`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=24;

--
-- AUTO_INCREMENT for table `messages`
--
ALTER TABLE `messages`
  MODIFY `message_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `notifications`
--
ALTER TABLE `notifications`
  MODIFY `notification_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=188;

--
-- AUTO_INCREMENT for table `order_completed`
--
ALTER TABLE `order_completed`
  MODIFY `completed_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- AUTO_INCREMENT for table `order_delivery`
--
ALTER TABLE `order_delivery`
  MODIFY `delivery_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- AUTO_INCREMENT for table `order_packing`
--
ALTER TABLE `order_packing`
  MODIFY `packing_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=8;

--
-- AUTO_INCREMENT for table `order_received`
--
ALTER TABLE `order_received`
  MODIFY `received_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=13;

--
-- AUTO_INCREMENT for table `order_shipping`
--
ALTER TABLE `order_shipping`
  MODIFY `shipping_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- AUTO_INCREMENT for table `product`
--
ALTER TABLE `product`
  MODIFY `product_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=93;

--
-- AUTO_INCREMENT for table `product_feedback`
--
ALTER TABLE `product_feedback`
  MODIFY `feedback_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT for table `product_images`
--
ALTER TABLE `product_images`
  MODIFY `images_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=197;

--
-- AUTO_INCREMENT for table `product_info`
--
ALTER TABLE `product_info`
  MODIFY `product_info_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=54;

--
-- AUTO_INCREMENT for table `product_rating`
--
ALTER TABLE `product_rating`
  MODIFY `rating_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- AUTO_INCREMENT for table `product_specs`
--
ALTER TABLE `product_specs`
  MODIFY `specs_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=262;

--
-- AUTO_INCREMENT for table `product_variant_images`
--
ALTER TABLE `product_variant_images`
  MODIFY `images_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `seller_sales`
--
ALTER TABLE `seller_sales`
  MODIFY `sales_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- AUTO_INCREMENT for table `seller_vouchers`
--
ALTER TABLE `seller_vouchers`
  MODIFY `voucher_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `shop`
--
ALTER TABLE `shop`
  MODIFY `shop_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT for table `shop_info`
--
ALTER TABLE `shop_info`
  MODIFY `shop_info_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT for table `shop_listing`
--
ALTER TABLE `shop_listing`
  MODIFY `shop_listing_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=93;

--
-- AUTO_INCREMENT for table `user_account`
--
ALTER TABLE `user_account`
  MODIFY `user_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=17;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `admin_order_commission`
--
ALTER TABLE `admin_order_commission`
  ADD CONSTRAINT `admin_order_commission_ibfk_1` FOREIGN KEY (`order_id`) REFERENCES `buyer_order` (`order_id`) ON DELETE CASCADE,
  ADD CONSTRAINT `admin_order_commission_ibfk_2` FOREIGN KEY (`seller_id`) REFERENCES `user_account` (`user_id`) ON DELETE CASCADE;

--
-- Constraints for table `admin_sales`
--
ALTER TABLE `admin_sales`
  ADD CONSTRAINT `admin_sales_ibfk_1` FOREIGN KEY (`admin_id`) REFERENCES `user_account` (`user_id`) ON DELETE CASCADE,
  ADD CONSTRAINT `admin_sales_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `user_account` (`user_id`) ON DELETE CASCADE,
  ADD CONSTRAINT `admin_sales_ibfk_3` FOREIGN KEY (`order_id`) REFERENCES `buyer_order` (`order_id`) ON DELETE CASCADE;

--
-- Constraints for table `buyer_cart`
--
ALTER TABLE `buyer_cart`
  ADD CONSTRAINT `buyer_cart_ibfk_1` FOREIGN KEY (`product_id`) REFERENCES `product` (`product_id`) ON DELETE CASCADE,
  ADD CONSTRAINT `buyer_cart_ibfk_2` FOREIGN KEY (`buyer_id`) REFERENCES `user_account` (`user_id`) ON DELETE CASCADE;

--
-- Constraints for table `buyer_like`
--
ALTER TABLE `buyer_like`
  ADD CONSTRAINT `buyer_like_ibfk_1` FOREIGN KEY (`product_info_id`) REFERENCES `product` (`product_info_id`) ON DELETE CASCADE,
  ADD CONSTRAINT `buyer_like_ibfk_2` FOREIGN KEY (`buyer_id`) REFERENCES `user_account` (`user_id`) ON DELETE CASCADE;

--
-- Constraints for table `buyer_order`
--
ALTER TABLE `buyer_order`
  ADD CONSTRAINT `buyer_order_ibfk_1` FOREIGN KEY (`shop_id`) REFERENCES `shop` (`shop_id`) ON DELETE CASCADE,
  ADD CONSTRAINT `buyer_order_ibfk_2` FOREIGN KEY (`seller_id`) REFERENCES `user_account` (`user_id`) ON DELETE CASCADE,
  ADD CONSTRAINT `buyer_order_ibfk_3` FOREIGN KEY (`product_id`) REFERENCES `product` (`product_id`) ON DELETE CASCADE,
  ADD CONSTRAINT `buyer_order_ibfk_4` FOREIGN KEY (`buyer_id`) REFERENCES `user_account` (`user_id`) ON DELETE CASCADE;

--
-- Constraints for table `courier_sales`
--
ALTER TABLE `courier_sales`
  ADD CONSTRAINT `courier_sales_ibfk_1` FOREIGN KEY (`order_id`) REFERENCES `buyer_order` (`order_id`) ON DELETE CASCADE,
  ADD CONSTRAINT `courier_sales_ibfk_2` FOREIGN KEY (`courier_id`) REFERENCES `user_account` (`user_id`) ON DELETE CASCADE;

--
-- Constraints for table `login_attempts`
--
ALTER TABLE `login_attempts`
  ADD CONSTRAINT `login_attempts_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user_account` (`user_id`) ON DELETE CASCADE;

--
-- Constraints for table `messages`
--
ALTER TABLE `messages`
  ADD CONSTRAINT `messages_ibfk_1` FOREIGN KEY (`recipient_id`) REFERENCES `user_account` (`user_id`) ON DELETE CASCADE,
  ADD CONSTRAINT `messages_ibfk_2` FOREIGN KEY (`sender_id`) REFERENCES `user_account` (`user_id`) ON DELETE CASCADE;

--
-- Constraints for table `notifications`
--
ALTER TABLE `notifications`
  ADD CONSTRAINT `notifications_ibfk_1` FOREIGN KEY (`recipient_id`) REFERENCES `user_account` (`user_id`) ON DELETE CASCADE,
  ADD CONSTRAINT `notifications_ibfk_2` FOREIGN KEY (`sender_id`) REFERENCES `user_account` (`user_id`) ON DELETE CASCADE;

--
-- Constraints for table `order_completed`
--
ALTER TABLE `order_completed`
  ADD CONSTRAINT `order_completed_ibfk_1` FOREIGN KEY (`order_id`) REFERENCES `buyer_order` (`order_id`) ON DELETE CASCADE;

--
-- Constraints for table `order_delivery`
--
ALTER TABLE `order_delivery`
  ADD CONSTRAINT `order_delivery_ibfk_1` FOREIGN KEY (`order_id`) REFERENCES `buyer_order` (`order_id`) ON DELETE CASCADE,
  ADD CONSTRAINT `order_delivery_ibfk_2` FOREIGN KEY (`courier_id`) REFERENCES `user_account` (`user_id`) ON DELETE CASCADE;

--
-- Constraints for table `order_packing`
--
ALTER TABLE `order_packing`
  ADD CONSTRAINT `order_packing_ibfk_1` FOREIGN KEY (`order_id`) REFERENCES `buyer_order` (`order_id`) ON DELETE CASCADE;

--
-- Constraints for table `order_received`
--
ALTER TABLE `order_received`
  ADD CONSTRAINT `order_received_ibfk_1` FOREIGN KEY (`order_id`) REFERENCES `buyer_order` (`order_id`) ON DELETE CASCADE,
  ADD CONSTRAINT `order_received_ibfk_2` FOREIGN KEY (`buyer_id`) REFERENCES `user_account` (`user_id`) ON DELETE CASCADE;

--
-- Constraints for table `order_shipping`
--
ALTER TABLE `order_shipping`
  ADD CONSTRAINT `order_shipping_ibfk_1` FOREIGN KEY (`order_id`) REFERENCES `buyer_order` (`order_id`) ON DELETE CASCADE;

--
-- Constraints for table `product`
--
ALTER TABLE `product`
  ADD CONSTRAINT `product_ibfk_1` FOREIGN KEY (`product_info_id`) REFERENCES `product_info` (`product_info_id`) ON DELETE CASCADE;

--
-- Constraints for table `product_feedback`
--
ALTER TABLE `product_feedback`
  ADD CONSTRAINT `product_feedback_ibfk_1` FOREIGN KEY (`shop_id`) REFERENCES `shop` (`shop_id`),
  ADD CONSTRAINT `product_feedback_ibfk_2` FOREIGN KEY (`product_id`) REFERENCES `product` (`product_id`) ON DELETE CASCADE,
  ADD CONSTRAINT `product_feedback_ibfk_3` FOREIGN KEY (`sender_id`) REFERENCES `user_account` (`user_id`) ON DELETE CASCADE;

--
-- Constraints for table `product_images`
--
ALTER TABLE `product_images`
  ADD CONSTRAINT `product_images_ibfk_1` FOREIGN KEY (`product_info_id`) REFERENCES `product` (`product_info_id`) ON DELETE CASCADE;

--
-- Constraints for table `product_rating`
--
ALTER TABLE `product_rating`
  ADD CONSTRAINT `product_rating_ibfk_1` FOREIGN KEY (`shop_id`) REFERENCES `shop` (`shop_id`),
  ADD CONSTRAINT `product_rating_ibfk_2` FOREIGN KEY (`product_id`) REFERENCES `product` (`product_id`) ON DELETE CASCADE,
  ADD CONSTRAINT `product_rating_ibfk_3` FOREIGN KEY (`sender_id`) REFERENCES `user_account` (`user_id`) ON DELETE CASCADE;

--
-- Constraints for table `product_specs`
--
ALTER TABLE `product_specs`
  ADD CONSTRAINT `product_specs_ibfk_1` FOREIGN KEY (`product_info_id`) REFERENCES `product` (`product_info_id`) ON DELETE CASCADE;

--
-- Constraints for table `product_variant_images`
--
ALTER TABLE `product_variant_images`
  ADD CONSTRAINT `product_variant_images_ibfk_1` FOREIGN KEY (`product_id`) REFERENCES `product` (`product_id`) ON DELETE CASCADE;

--
-- Constraints for table `seller_sales`
--
ALTER TABLE `seller_sales`
  ADD CONSTRAINT `seller_sales_ibfk_1` FOREIGN KEY (`order_id`) REFERENCES `buyer_order` (`order_id`) ON DELETE CASCADE,
  ADD CONSTRAINT `seller_sales_ibfk_2` FOREIGN KEY (`seller_id`) REFERENCES `user_account` (`user_id`) ON DELETE CASCADE;

--
-- Constraints for table `seller_vouchers`
--
ALTER TABLE `seller_vouchers`
  ADD CONSTRAINT `seller_vouchers_ibfk_1` FOREIGN KEY (`seller_id`) REFERENCES `user_account` (`user_id`) ON DELETE CASCADE;

--
-- Constraints for table `shop`
--
ALTER TABLE `shop`
  ADD CONSTRAINT `shop_ibfk_1` FOREIGN KEY (`shop_info_id`) REFERENCES `shop_info` (`shop_info_id`) ON DELETE CASCADE,
  ADD CONSTRAINT `shop_ibfk_2` FOREIGN KEY (`seller_id`) REFERENCES `user_account` (`user_id`) ON DELETE CASCADE;

--
-- Constraints for table `shop_listing`
--
ALTER TABLE `shop_listing`
  ADD CONSTRAINT `shop_listing_ibfk_1` FOREIGN KEY (`shop_id`) REFERENCES `shop` (`shop_id`) ON DELETE CASCADE,
  ADD CONSTRAINT `shop_listing_ibfk_2` FOREIGN KEY (`seller_id`) REFERENCES `user_account` (`user_id`) ON DELETE CASCADE,
  ADD CONSTRAINT `shop_listing_ibfk_3` FOREIGN KEY (`product_id`) REFERENCES `product` (`product_id`) ON DELETE CASCADE;

--
-- Constraints for table `user_account`
--
ALTER TABLE `user_account`
  ADD CONSTRAINT `user_account_ibfk_1` FOREIGN KEY (`personal_id`) REFERENCES `account_personal_info` (`personal_id`) ON DELETE CASCADE,
  ADD CONSTRAINT `user_account_ibfk_2` FOREIGN KEY (`address_id`) REFERENCES `account_address_info` (`address_id`) ON DELETE CASCADE,
  ADD CONSTRAINT `user_account_ibfk_3` FOREIGN KEY (`contact_id`) REFERENCES `account_contact_info` (`contact_id`) ON DELETE CASCADE,
  ADD CONSTRAINT `user_account_ibfk_4` FOREIGN KEY (`valid_id`) REFERENCES `account_valid_info` (`valid_id`) ON DELETE CASCADE,
  ADD CONSTRAINT `user_account_ibfk_5` FOREIGN KEY (`login_id`) REFERENCES `account_login_info` (`login_id`) ON DELETE CASCADE,
  ADD CONSTRAINT `user_account_ibfk_6` FOREIGN KEY (`business_id`) REFERENCES `account_business_info` (`business_id`) ON DELETE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
