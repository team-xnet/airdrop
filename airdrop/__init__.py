"""XNET & XSPUNKS airdrop utility.                     """
"""Author: spunk-developer <xspunk.developer@gmail.com>"""

from string import Template

from rich.console import Console
from dataclasses  import dataclass
from rich.theme   import Theme

__app_version__ = "1.0.0"
__app_name__    = "airdrop"

CONSOLE_THEME = Theme(
    {
        "prominent": "bright_yellow",
        "success":   "bright_green bold",
        "error":     "bright_red bold",
        "info":      "bright_blue bold",
        "warn":      "bright_magenta bold",
        "m":         "yellow",
        "y":         "green",
        "n":         "red",
    }
)


@dataclass(frozen=True)
class I18NPreflight():

    # Terms of Use
    terms_message = "Type (Y)es if you agree to these terms, or (N)o if you wish to exit the program: "
    terms_error   = "Please enter either (Y)es or (N)o: "

    # Rendered banner title
    banner_subtitle    = "Made using XRP, Python, and a LOT of coffee by XNET."
    banner_description = "Thank you for using XNET Airdrop! Airdrop is a small utility program built to make the most tedious aspect of initial token distribution (Commonly known as airdropping) easier — The calculation aspect of it. Airdrop will automatically fetch all trustlines set against the desired currency so it can then calculate the total yield per trustline token, which is then finally filtered and organized into a table for you to use as the total distribution table for the distribution itself.\n\n"
    banner_note        = "Airdro CAN OPTIONALLY send tokens if the user chooses to, however this is NOT required. Distributing tokens based on the generated output data is a separate function of the program.\n\n"
    banner_disclaimer  = "DISCLAIMER: We (XNET and all XNET affiliated entities) are not responsible for any loss of funds, or any damages of any kind that result in the use of this program. We also ask all users to double check all generated output for validity and correctness. We do not guarantee the resulting data of any kind being factually correct.\n"

    # Metadata fetch
    metadata_fetch     = "[[info]WORKING[/info]] Fetching prequisite metadata..."
    error_fetch_failed = "[n]✗[/n] [[error]FAIL[/error]] Failed fetching prequisite metadata. Make sure you have an active internet connection, and that XRPLMeta services are available."

    # Input yielding address
    enter_yielding           = Template('[prominent](${step}/${maximum})[/prominent] Enter yield token issuing address or "XRP" for XRP yield: ')
    error_yielding_invalid   = Template('Issuing address "${address}" isn\'t a known token issuing address. Please make sure you have entered the address correctly or input "XRP" for XRP yield and try again: ')
    error_yielding_missing   = Template('[n]✗[/n] [[error]FAIL[/error]] Yielding address "${address}" isn\'t a known token issuing address. Please make sure you have entered the address correctly, and that one or more tokens issued by this address has a trust level of 1 or greater on the XRPL. If the intent was to use XRP as the yielding token, simply enter "XRP" as the yielding token parameter')
    error_yielding_overwrite = Template('[n]✗[/n] [[error]FAIL[/error]] Yielding issuing address "${address}" cannot be set, as overwriting the yielding issuing address is forbidden')

    # Input issuing address
    choose_token           = Template('We detected [prominent]${total}[/prominent] tokens issued by address [prominent]${address}[/prominent]:\n\n${tokens}\n\nPlease enter the number of one from the list above')
    enter_issuer           = Template('[prominent](${step}/${maximum})[/prominent] Enter source token issuing address: ')
    error_issuer_invalid   = Template('Issuing address "${address}" isn\'t a known token issuing address. Please make sure you have entered the address correctly and try again: ')
    error_issuer_missing   = Template('[n]✗[/n] [[error]FAIL[/error]] Issuing address "${address}" isn\'t a known token issuing address. Please make sure you have entered the address correctly, and that one or more tokens issued by this address has a trust level of 1 or greater on the XRPL')
    error_issuer_overwrite = Template('[n]✗[/n] [[error]FAIL[/error]] Source issuing address "${address}" cannot be set, as overwriting the source issuing address is forbidden')

    # Input budget validation
    enter_balance    = Template('[prominent](${step}/${maximum})[/prominent] Enter the total airdrop budget')
    error_conversion = Template('[n]✗[/n] [[error]FAIL[/error]] Could not converty input "${value}" into a number')
    error_overwrite  = "[n]✗[/n] [[error]FAIL[/error]] Cannot overwrite supply budget, as it has already been defined"
    error_minimum    = Template('[n]✗[/n] [[error]FAIL[/error]] Input "${value}" must be larger than 0')
    error_maximum    = Template('[n]✗[/n] [[error]FAIL[/error]] Input "${value}" cannot be larger than maximum allowed integer 100000000000000000')

    # Output CSV file
    confirm_csv      = Template('[prominent](${step}/${maximum})[/prominent] Once the airdrop has finished calculating, would you like to save the results into a CSV file? If not, the result of the calculations is printed into console as a table')
    choose_path      = "Where would you like to save the CSV file?\n\n1. Desktop\n2. Documents\n3. Custom...\n\nEnter choice"
    custom_path      = "Enter custom save path for the output CSV file"
    error_empty_path = Template('Path "${path}" is not valid. Please make sure it follows the path specification of your operating system, and that it is not empty!')

    # Confirm options
    confirm_preflight_calculate  = Template('\n - Issued token: ${issuing}\n - Yield token: ${yielding}\n - Total budget: ${budget}\n - Output CSV & metadata files path: ${csv}\n\nIs this OK?')
    confirm_preflight_distribute = Template('\n - Distributed token: ${token}\n - Cold wallet: ${wallet}\n - Input data files path: ${filepaths}\n\nIs this OK? (Y/n):')

    # Input data path
    choose_data        = Template('[prominent](${step}/${maximum})[/prominent] Where are the input data files located?\n\n1. Desktop\n2. Documents\n3. Custom...\n\nEnter choice')
    enter_data         = 'Enter the path that includes both meta and data files: '
    error_data_invalid = Template('Path "${datapath}" doesn\'t include either the data or the meta file(s). Please make sure you have entered the path correctly, that you have the required permissions to read files within the given path and try again: ')
    error_filepaths    = Template('[n]✗[/n] [[error]FAIL[/error]] Couldn\'t locate [prominent]${filetype}[/prominent] at [prominent]${filepath}[/prominent]. Please make sure the file exists, that you have the required permissions to read the file and that the name hasn\'t been altered.')

    # Input seed
    enter_seed         = Template('[prominent](${step}/${maximum})[/prominent] Enter cold wallet seed: ')
    enter_seed_invalid = Template('Wallet seed [prominent]${seed}[/prominent] isn\'t a valid wallet seed, please double check the seed and try again: ')
    error_seed         = Template('[n]✗[/n] [[error]FAIL[/error]] Seed [prominent]${seed}[/prominent] isn\'t a valid wallet seed. Please check the seed and try again')

@dataclass(frozen=True)
class I18NSteps():

    # Setup
    error_clients = "[n]✗[/n] [[error]FAIL[/error]] Could not connect to any XRPL public API. This could be due to rate limiting, or due to the lack of a stable internet connection"

    # Yield calculation
    yield_sum            = "[[info]WORKING[/info]] Summing up the total balance for all trustlines..."
    yield_result         = "[[info]WORKING[/info]] Calculating total yield for all trustlines..."
    yield_result_account = Template('[[info]WORKING[/info]] Calculating total yield for [prominent]${address}[/prominent]...')

    # Trustline fetch
    trustlines_fetch         = Template('[[info]WORKING[/info]] Fetching trustlines for address [prominent]${address}[/prominent]...')
    trustlines_fetch_success = Template('[y]✓[/y] [[success]SUCCESS[/success]] Successfully fetched [prominent]${count}[/prominent] trustlines set for issuing address [prominent]${address}[/prominent] in [prominent]${delta}[/prominent]')
    error_trustline_fetch    = Template('[n]✗[/n] [[error]FAIL[/error]] Failed fetching trustlines for address [prominent]${address}[/prominent]! Please make sure you have an active internet connection, and that the issuing token in question has one or more trustlines set against it')

    # Balances fetch
    balances_fetch         = Template('[[info]WORKING[/info]] Fetching [prominent]${token}[/prominent] balances for [prominent]${count}[/prominent] trustlines, this may take a while...')
    balances_fetch_account = Template('[[info]WORKING[/info]] Fetching [prominent]${token}[/prominent] balance for trustline address [prominent]${address}[/prominent]...')
    balances_fetch_success = Template('[y]✓[/y] [[success]SUCCESS[/success]] Successfully fetched [prominent]${token}[/prominent] balances for [prominent]${count}[/prominent] trustlines in [prominent]${delta}[/prominent]')
    error_balances         = Template('[[info]WORKING[/info]] Failed fetching balance for trustline [prominent]${address}[/prominent] due to rate limiting, waiting for [prominent]${delta}[/prominent] seconds before trying again...')

    # Print yield
    error_saving_csv = Template('[n]✗[/n] [[error]FAIL[/error]] Could not save output CSV or metadata file(s) to path [prominent]${path}[/prominent]. Please make sure you have correct permissions to write to this location and try again')
    print_subtitle   = "Finished airdrop calculations!"
    print_header     = "Total airdrop yield"

    # Input data validation
    input_meta_validation = "[[info]WORKING[/info]] Validating input metadata file..."
    input_data_validation = "[[info]WORKING[/info]] Validating input data file..."
    input_data_success    = "[y]✓[/y] [[success]SUCCESS[/success]] Successfully validated input meta & data files"
    error_input_meta      = "[n]✗[/n] [[error]FAIL[/error]] Could not validate metadata file due to missing or modified contents. Please try to restore the file's contents back to it's original output state and try again"
    error_input_data      = "[n]✗[/n] [[error]FAIL[/error]] Could not validate data file due to missing or modified contents. Please try to restore the file's contents back to it's original output state and try again"

    # Actual data validation
    validate_filtered         = "[[info]WORKING[/info]] Validating filtered trustlines..."
    validate_filtered_success = Template('[y]✓[/y] [[success]SUCCESS[/success]] Succesfully validated filtered trustlines: [prominent]${trustlines}[/prominent] total trustlines, [prominent]${filtered}[/prominent] filtered with a diffrence of [prominent]${difference}[/prominent]')
    error_validate_filtered   = "[n]✗[/n] [[error]FAIL[/error]] Filtered trustlines don't match reported difference in metadata"

    # Validate calculation
    validate_calculation         = "[[info]WORKING[/info]] Validating airdrop calculations..."
    validate_calculation_success = Template('[y]✓[/y] [[success]SUCCESS[/success]] Successfully validated [prominent]${token}[/prominent] airdrop calculations')
    error_validate_calculation   = Template('[n]✗[/n] [[error]FAIL[/error]] Could not validate [prominent]${token}[/prominent] airdrop calculations. Either the data has been corrupted in some way, or the declared metadata sum is wrong. Expected sum to be [prominent]${expected}[/prominent, but got [prominent]${got}[/prominent]')

    # Validate ratio
    validate_ratio         = "[[info]WORKING[/info]] Validating airdrop ratio..."
    validate_ratio_success = Template('[y]✓[/y] [[success]SUCCESS[/success]] Successfully validated [prominent]${token}[/prominent] airdrop ratio')
    error_validate_ratio   = Template('[n]✗[/n] [[error]FAIL[/error]] Could not validate [prominent]${token}[/prominent] ratio due to either the data being corrupted or the metadata being tampered with. Expected to get ratio [prominent]${expected}[/prominent, but got ratio [prominent]${got}[/prominent]')

    # Token distribution
    distribute_working = Template('[[info]WORKING[/info]] Sending [prominent]${amount} ${token}[/prominent] to [prominent]${destination}[/prominent]...')
    distribute_success = Template('[y]✓[/y] [[success]SUCCESS[/success]] Successfully sent [prominent]${amount} ${token}[/prominent] to [prominent]${destination}[/prominent]')
    distribute_error = Template('[n]✗[/n] [[error]FAIL[/error]] Could not send [prominent]${amount} ${token}[/prominent] to [prominent]${destination}[/prominent]')
    distribute_warn  = Template('[m]![/m] [[warn]WARNING[/warn]] Failed sending [prominent]${token}[/prominent] to [prominent]${amount}[/prominent] trustlines. Failed trustline information has been saved in [prominent]${log}[/prominent]')

    # Distribution summary
    summary_table_header = "Failed Distribution Trustlines"

@dataclass(frozen=True)
class I18NRehydrate:

    metadata_cache = "We detected cached XRPL Meta metadata on disk. Would you like to use the previously cached data? (Y/n): "
    metadata_error = "Please enter either (Y)es or (N)o: "


@dataclass(frozen=True)
class I18NBase():
    preflight = I18NPreflight()
    rehydrate = I18NRehydrate()
    steps     = I18NSteps()

def t(str: Template, **kwargs) -> str:
    return str.substitute(kwargs)


console = Console(color_system="auto", theme=CONSOLE_THEME)
i18n    = I18NBase()
