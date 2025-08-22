{{ APPLICATION_NAME }} uses Gamry Framework's **GamryCOM** interface to interact with Gamry instruments. This feature is completely optional.

- You can enable/disable Gamry support by clicking the checkbox.
    - If Gamry integration is enabled, Quincy will take longer to launch (as it needs to load **GamryCOM**).

- For Gamry features to work, {{ APPLICATION_NAME }} needs to know where **GamryCOM** is. You can specify the executable location using the file dialog button.

- If {{ APPLICATION_NAME }} cannot load **GamryCOM**, it will prompt you to disable Gamry features.

- When Gamry features are disabled, Gamry-related items will not show up in the application. This means Gamry sequence options are hidden and scripts that are loaded into the sequence builder will have their Gamry items ignored.

*Settings are loaded the next time {{ APPLICATION_NAME }} launches.*
