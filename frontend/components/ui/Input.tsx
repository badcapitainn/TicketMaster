import { forwardRef, InputHTMLAttributes } from "react";

export interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
}

const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ className = "", label, error, id, ...props }, ref) => {
    return (
      <div className="w-full">
        {label && (
          <label htmlFor={id} className="block text-sm font-medium text-gray-700 mb-1">
            {label}
          </label>
        )}
        <input
          id={id}
          ref={ref}
          className={`appearance-none block w-full px-3 py-2 border ${
            error ? "border-red-300 placeholder-red-300 focus:ring-red-500 focus:border-red-500" : "border-gray-300 placeholder-gray-400 focus:ring-primary focus:border-primary"
          } rounded-md shadow-sm bg-white focus:outline-none focus:ring-2 sm:text-sm transition-shadow ${className}`}
          {...props}
        />
        {error && <p className="mt-1 text-sm text-red-600">{error}</p>}
      </div>
    );
  }
);

Input.displayName = "Input";
export default Input;
