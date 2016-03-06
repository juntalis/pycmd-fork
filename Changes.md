Cataloging the changes I've made to the original PyCmd source code:

 * Changes made to [console.py]:
    * Expanded the `ColorOutputStream` class, adding a few members that you'd
      expect to see on `sys.stdout`.
    * Removed the dependency on the PyWin32 `win32console` module by making the
      following updates:
        * Reimplemented used `win32console` API using ctypes: [win32console.py]
        * Removed [console.py]'s existing usages of the `ctypes` module, 
          replacing them with new implementations in [win32console.py]. The new
          implementations add:
            * Error checking for the Win32 API call. Failed calls will result in
              a `ctypes.WinError` exception being raised.
            * Function prototype caching so that `ctypes` doesn't have to 
              determine the correct converters to use on its own. (Does this
              happen with every call, or is it cached after the first call?)
        * Changed `ctypes.pointer` calls to `ctypes.byref` calls where
          appropriate. Reasoning:
            * From the [official documentation][ctypes-byref-vs-pointer]:
              
              > pointer does a lot more work since it constructs a real pointer
              > object, so it is faster to use byref if you don't need the
              > pointer object in Python itself
 * Changes made to [InputState.py]:
    * No actual changes to the original PyCmd source code were necessary for
      this one. From PyCmd's perspective, the new ctypes implementations in
      [win32clipboard.py] are functionally equivalent to the pywin32 versions.

[console.py]: console.py
[InputState.py]: InputState.py
[win32console.py]: win32console.py
[win32clipboard.py]: win32clipboard.py

[ctypes-byref-vs-pointer]: https://docs.python.org/release/2.5.2/lib/ctypes-passing-pointers.html
