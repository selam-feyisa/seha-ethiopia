function ErrorMessage({ message = 'Something went wrong. Please try again.' }) {
  return (
    <div className="bg-red-50 border border-red-300 text-red-700 rounded-lg px-4 py-3 my-4 text-sm">
      ⚠️ {message}
    </div>
  );
}
export default ErrorMessage;